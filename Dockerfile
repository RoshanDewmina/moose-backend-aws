FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

COPY requirements.txt requirements.txt

RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /src

RUN useradd -m myuser
USER myuser

WORKDIR /src

CMD ["python", "main.py"]

#RUN python3 -m uvicorn --help
#ENV APP_DIR=/
#ENV APP=app:app
#ENTRYPOINT uvicorn $APP --app-dir $APP_DIR --host 0.0.0.0 --port 8000 --reload
