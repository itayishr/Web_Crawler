import hashlib
import json
import logging
import time
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from starlette.responses import JSONResponse
import redis
import validators

from common import config, enums
from worker import process_crawl_request_task


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/crawler', tags=['Web Crawler'])
redis_client = redis.Redis(host='redis', port=config.REDIS_PORT)


class ResponseModel(BaseModel):
    status: enums.ResponseStatus


def hash_timestamp_and_url(page_url: str, timestamp: str):
    logger.info(f'Creating hash for URL:{page_url},timestamp:{timestamp}')
    appended = page_url + timestamp
    hash_object = hashlib.md5(appended.encode())
    return hash_object.hexdigest()


@router.post("/process_crawl", status_code=200)
async def process_crawl_request(page_url: str) -> JSONResponse:
    """
    Create a crawl request for the passed URL.
    """
    # Validate URL address before continuing.
    if not validators.url(page_url):
        logger.info(f'Invalid URL:{page_url}')
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'Invalid URL')

    timestamp = str(round(time.time() * 1000))
    hash = hash_timestamp_and_url(page_url, timestamp)
    logger.info(f'Sending process_crawl_request task')
    process_crawl_request_task.delay(hash=hash, page_url=page_url, timestamp=timestamp)
    return JSONResponse({"crawl_id": hash})


@router.get("/crawl_status/{crawl_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def get_crawl_status(crawl_id: str):
    """
    Return the status of the submitted Task
    """
    redis_result = redis_client.get(crawl_id)
    if redis_result is None:
        logger.info(f'Task {crawl_id} not found.')
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Task not found')

    redis_result_json = json.loads(redis_result.decode())
    response_json = {}
    response_status = redis_result_json['status']
    logger.info(f'Status of request {crawl_id}: {response_status}')
    response_json['status'] = response_status

    if response_json['status'] == enums.ResponseStatus.COMPLETE.value:
        logger.info('Task is done, providing URL')
        response_json['file_url'] = redis_result_json['file_url']

    return JSONResponse(status_code=status.HTTP_200_OK, content=response_json)
