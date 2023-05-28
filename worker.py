from celery import Celery
import os
import requests
from elasticsearch import Elasticsearch
import redis
from common import enums

celery = Celery()
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5674/")
ELASTIC_HOST: str = os.environ.get("ELASTICSEARCH_HOSTS", "http://localhost:9200")
es = Elasticsearch(ELASTIC_HOST)
REDIS_PORT: int = os.environ.get("REDIS_PORT", "6780")
redis_client = redis.Redis(host='redis', port=REDIS_PORT)


@celery.task(name='process_crawl_request_task')
def process_crawl_request_task(hash, page_url, timestamp):
    # Get raw HTML content
    # Store in Redis in the following format : {hash, status}
    redis_client.set(hash, enums.ResponseStatus.ACCEPTED.name)
    html_content = requests.get(page_url).text
    save_html_to_db.delay(hash, page_url, timestamp, html_content)
    print('Saving to redis')


@celery.task(name='get_task_status')
def get_task_status(hash):
    return redis_client.get(hash)


@celery.task(name='save_html_to_db')
def save_html_to_db(hash: str, page_url: str, timestamp: str, html_content: str):
    redis_client.set(hash, enums.ResponseStatus.RUNNING.name)
    html_json = {'url': str(page_url), 'hash': hash, 'timestamp': timestamp, 'page_content': html_content}
    # Send raw HTML content to another queue for elasticsearch db.
    print("Indexing")
    resp = es.index(index='html', document=html_json)
    redis_client.set(hash, enums.ResponseStatus.COMPLETE.name)
