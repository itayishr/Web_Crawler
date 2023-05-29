import os

# Environment variables
ELASTIC_HOST: str = os.environ.get("ELASTICSEARCH_HOSTS", "http://localhost:9200")
REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT: int = os.environ.get("REDIS_PORT", "6780")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5674/")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "html_storage_bucket")

# RabbitMQ Queue Names
PROCESS_CRAWL_REQUEST_QUEUE_NAME = "crawl_request_queue"
SAVE_HTML_TO_DB_QUEUE_NAME = "html_extraction_queue"
