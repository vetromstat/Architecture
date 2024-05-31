FROM python:3.11
WORKDIR /rest_api

RUN pip install swagger_ui sqlalchemy psycopg2-binary "fastapi["all"]"

COPY . /rest_api

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]