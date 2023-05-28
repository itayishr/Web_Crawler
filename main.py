from fastapi import FastAPI
from routers import crawler_routes

app = FastAPI(
    title="Web Crawler Rest API",
    description="Web Crawler service implemented with FastAPI, to supply the Web Crawler with new requests, using RabbitMQ as a message broker and Celery as a consumer manager.",
    version="1.0.0",
)
app.include_router(crawler_routes.router)
