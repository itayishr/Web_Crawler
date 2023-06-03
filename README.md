# Web Crawler API

This project implements a web crawler API with two endpoints using FastAPI, RabbitMQ, and Celery. The API allows users to submit a crawl request, which returns a unique crawl ID, and check the status of a crawl request using the crawl ID.

Please refer to https://itayishr.atlassian.net/l/cp/UVn02psk for further explanation about my thought process. 

## Technologies Used

- FastAPI: A modern, fast (high-performance) web framework for building APIs with Python.
- RabbitMQ: A message broker that enables communication between the API and the Celery worker.
- Celery: A distributed task queue system for asynchronous processing.
- Elasticsearch: A search engine used for storing HTML content.
- Redis: A key-value caching mechanism used for storing crawl request status for fast responses.
- S3 (Mocked with Moto): A storage service used for storing HTML files (mocked using Moto).

## Design 
![Crawler_Task_Design drawio(1)](https://github.com/itayishr/Web_Crawler/assets/37871040/411bc182-5ba5-43b6-9ccd-37b810b3f336)

## Installation 

1. Clone the repository:

```bash
git clone https://github.com/itayishr/Web_Crawler.git
```

2. Install Docker and docker-compose on machine.
3. Build the docker environment:
```
cd Web_Crawler
docker-compose build
```
4. Run the docker containers:
```
docker-compose up -d 
```
   
## API Endpoints

### Process Crawl Request

#### Endpoint: 
```POST /crawler/process_crawl```

#### Description: 
Submits a crawl request for a given URL.

#### Request Body:

```json

{
  "url": "https://example.com"
}
```

#### Response Body:

```json

{
  "crawl_id": "unique-crawl-id"
}
```

### Check Crawl Status

#### Endpoint: 

```GET /crawler/crawl_status/{crawl_id}```

#### Description: 

Retrieves the status of a crawl request using the provided crawl ID.

#### Response Body:

```json
{
  "crawl_id": "unique-crawl-id",
  "status": "completed",
  "result_url": "https://s3-bucket-url/file-path"
}
```

## Access the Swagger documentation:

Open your web browser and visit http://localhost:8010/docs to access the Swagger documentation for the API. 
You can explore the available endpoints, make requests, and view responses directly from the Swagger UI.

# Development

The API layer is implemented using FastAPI, which provides a simple way to define routes and request handlers.
RabbitMQ is used as the message broker to facilitate communication between the API and the Celery worker.
Celery is used to handle the asynchronous processing of crawl requests and processing.

It receives crawl requests from the API, performs the necessary tasks (e.g., extracting HTML content, saving it to Elasticsearch,
and storing the file in S3), and updates the crawl status in Redis.

Elasticsearch is used to store the HTML content, allowing efficient searching and retrieval.
Redis is used to store the crawl request status. It is updated by the Celery worker at various stages of processing.

S3 (mocked with Moto) is used as a storage service to save the HTML files associated with the crawl requests.

# License

This project is licensed under the MIT License.
Feel free to copy the code and use it as the README for your project.
