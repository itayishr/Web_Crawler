import logging
import requests
import json
import elasticsearch
from celery import Celery
from elasticsearch import Elasticsearch
from external_services import storage
import redis
from common import enums, config

# Configure logging
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery and config to integrate with RabbitMQ
celery = Celery()
celery.conf.broker_url = config.CELERY_BROKER_URL

# Initialize Elastic and Redis clients
es = Elasticsearch(config.ELASTIC_HOST)
redis_client = redis.Redis(host='redis', port=config.REDIS_PORT)

# Initialize S3 Storage and create new bucket for HTML Storage
storage = storage.StorageWrapper()


@celery.task(name='process_crawl_request_task')
def process_crawl_request_task(hash, page_url, timestamp):
    # Store in Redis in the following format: {hash, status}
    redis_client.set(hash, enums.ResponseStatus.ACCEPTED.name)
    save_html_to_db_task.delay(hash, page_url, timestamp)
    logger.info('Saving to redis')


@celery.task(name='save_html_to_db_task')
def save_html_to_db_task(hash: str, page_url: str, timestamp: str):
    redis_client.set(hash, enums.ResponseStatus.RUNNING.name)
    # Get HTML Content from URL
    html_content = requests.get(page_url).text
    # Handle the HTML content before saving to the database.
    html_json = {'url': str(page_url), 'hash': hash, 'timestamp': timestamp, 'page_content': html_content}
    try:
        response = es.index(index='html', document=html_json)
        if response['result'] == 'created':
            # Successful indexing
            logger.info('Document indexed successfully.')
            result_url = storage.upload_html_file(content=html_content, task_hash=hash)
            # Store HTML File in S3 Bucket and set the task as complete
            # Prepare response JSON for Redis storage
            result = {'status': enums.ResponseStatus.COMPLETE.name, 'file_url': result_url}
            json_string = json.dumps(result)
            logger.info(result)
            redis_client.set(hash, json_string)
        else:
            # Error occurred during indexing
            logger.error('Error indexing document: %s', response)
    except elasticsearch.BadRequestError as e:
        # Exception occurred during indexing
        logger.exception('Exception occurred during indexing: %s', str(e))
        redis_client.set(hash, enums.ResponseStatus.ERROR.name)
