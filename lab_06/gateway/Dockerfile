FROM python:3.11

WORKDIR /arch/gateway

RUN pip install circuitbreaker fastapi[all] pydantic aiohttp pyjwt

COPY . /arch/gateway/

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]