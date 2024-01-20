
FROM python:3.8

WORKDIR /webapp

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn schedule pydantic psycopg2-binary websockets jinja2

COPY ./webapp /webapp
COPY ../db /db

CMD ["python", "webapp.py"]
