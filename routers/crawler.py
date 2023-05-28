from starlette.responses import JSONResponse
from fastapi import APIRouter
import hashlib
import time
from worker import process_crawl_request_task, get_task_status
from common import enums
import os
import redis

router = APIRouter(prefix='/crawler', tags=['Web Crawler'], responses={404: {"description": "Not found"}})
REDIS_PORT: int = os.environ.get("REDIS_PORT", "6780")
redis_client = redis.Redis(host='redis', port=REDIS_PORT)

def hash_timestamp_and_url(page_url: str, timestamp: str):
    appended = page_url + timestamp
    hash_object = hashlib.md5(appended.encode())
    return hash_object.hexdigest()


@router.post("/process_crawl")
async def process_crawl_request(page_url: str) -> JSONResponse:
    """
    Return the List of universities for the countries for e.g ["turkey","india","australia"] provided
    in input in a async way. It just returns the task id, which can later be used to get the result.
    """
    # TODO add processing logic
    timestamp = str(round(time.time() * 1000))
    hash = hash_timestamp_and_url(page_url, timestamp)
    process_crawl_request_task.delay(hash=hash,page_url=page_url,timestamp=timestamp)
    return JSONResponse({"crawl_id": hash})


@router.get("/crawl_status/{crawl_id}", response_model=enums.ResponseStatus)
async def get_crawl_status(crawl_id: str):
    """
    Return the status of the submitted Task
    """
    status = redis_client.get(crawl_id).decode()
    return JSONResponse({"Status": enums.ResponseStatus(status).name}, status_code=200)
