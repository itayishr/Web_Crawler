from celery import Celery
import os

celery = Celery()
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5674/")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "amqp://guest:guest@localhost:5674/")


@celery.task(queue='crawl_requests')
def process_crawl_request_task(hash, page_url, timestamp):
    print('here')
    # Get raw HTML content
    # html_content = requests.get(page_url).text
    # es = Elasticsearch(ELASTIC_HOST)
    # html_json = json.dumps({'url': str(page_url),'hash':hash, 'timestamp':timestamp,'page_content': html_content})
    # # Send raw HTML content to another queue for elasticsearch db.
    # resp = es.index(index='html', document=html_json)
    # # Store in Redis in the following format : {url, hash_id}
    # redis_client = redis.Redis(host='redis_cache', port=REDIS_PORT)
    # crawl_status = schemas.ResponseStatus.COMPLETE
    # print('Saving to redis')
    # redis_client.set(hash,crawl_status)
