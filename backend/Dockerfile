FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

USER app

# One worker, since rate limits are counted in memory per process; more
# workers or instances would need shared storage such as Redis.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--worker-class", "gthread", "--threads", "16", "--timeout", "60", "--access-logfile", "-", "run:app"]
