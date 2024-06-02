FROM python:3.11
WORKDIR /arch/deliveries

RUN pip install fastapi[all] pymongo motor pydantic aiohttp pyjwt

COPY . /arch/deliveries/ 

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]