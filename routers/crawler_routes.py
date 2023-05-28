import http
from starlette.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status
import hashlib
import time

import common.enums
from worker import process_crawl_request_task
from common import config
import redis
import validators
from pydantic import BaseModel

router = APIRouter(prefix='/crawler', tags=['Web Crawler'])
redis_client = redis.Redis(host='redis', port=config.REDIS_PORT)


class ResponseModel(BaseModel):
    status: common.enums.ResponseStatus


def hash_timestamp_and_url(page_url: str, timestamp: str):
    appended = page_url + timestamp
    hash_object = hashlib.md5(appended.encode())
    return hash_object.hexdigest()


@router.post("/process_crawl", status_code=200)
async def process_crawl_request(page_url: str) -> JSONResponse:
    """
    Create a crawl request for the passed URL.
    """
    # Validate url address before continuing.
    if not validators.url(page_url):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'Invalid URL')
    timestamp = str(round(time.time() * 1000))
    hash = hash_timestamp_and_url(page_url, timestamp)
    process_crawl_request_task.delay(hash=hash, page_url=page_url, timestamp=timestamp)
    return JSONResponse({"crawl_id": hash})


@router.get("/crawl_status/{crawl_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def get_crawl_status(crawl_id: str):
    """
    Return the status of the submitted Task
    """
    redis_result = redis_client.get(crawl_id)
    if redis_result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Task not found')
    return JSONResponse(status_code=status.HTTP_200_OK, content={"Status": redis_result.decode()})
