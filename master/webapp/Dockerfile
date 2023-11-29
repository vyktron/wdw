
FROM python:3.8

WORKDIR /webapp

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn schedule pydantic

COPY . /webapp
COPY ../db /db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
