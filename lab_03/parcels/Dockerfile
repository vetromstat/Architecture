FROM python:3.11
WORKDIR  /arch/parcels/ 

RUN pip install fastapi[all] pymongo motor pydantic

COPY . /arch/parcels/   

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]