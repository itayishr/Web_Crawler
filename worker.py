import elasticsearch
from celery import Celery
import requests
from elasticsearch import Elasticsearch

import redis
from common import enums, config


celery = Celery()
celery.conf.broker_url = config.CELERY_BROKER_URL
es = Elasticsearch(config.ELASTIC_HOST)
redis_client = redis.Redis(host='redis', port=config.REDIS_PORT)


@celery.task(name='process_crawl_request_task')
def process_crawl_request_task(hash, page_url, timestamp):
    # Store in Redis in the following format : {hash, status}
    redis_client.set(hash, enums.ResponseStatus.ACCEPTED.name)
    save_html_to_db_task.delay(hash, page_url, timestamp)
    print('Saving to redis')


@celery.task(name='save_html_to_db_task')
def save_html_to_db_task(hash: str, page_url: str, timestamp: str):
    redis_client.set(hash, enums.ResponseStatus.RUNNING.name)
    # Get HTML Content from url
    html_content = requests.get(page_url).text
    # Handle the html content before saving to db.
    html_json = {'url': str(page_url), 'hash': hash, 'timestamp': timestamp, 'page_content': html_content}
    try:
        response = es.index(index='html', document=html_json)
        if response['result'] == 'created':
            # Successful indexing
            print('Document indexed successfully.')
            redis_client.set(hash, enums.ResponseStatus.COMPLETE.name)
        else:
            # Error occurred during indexing
            print('Error indexing document:', response)
    except elasticsearch.BadRequestError as e:
        # Exception occurred during indexing
        print('Exception occurred during indexing:', str(e))
        redis_client.set(hash, enums.ResponseStatus.ERROR.name)
