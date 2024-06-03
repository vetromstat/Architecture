FROM python:3.11
WORKDIR /arch/init

RUN pip install sqlalchemy psycopg2-binary motor pydantic passlib

COPY . /arch/init/ 

ENTRYPOINT ["bash", "-c", "python3 postgres_init.py && python3 mongo_init.py"]
