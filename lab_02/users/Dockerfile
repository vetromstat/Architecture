FROM python:3.11
WORKDIR /arch/users

RUN pip install swagger_ui sqlalchemy psycopg2-binary "fastapi["all"]"

COPY . /arch/users/  

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]