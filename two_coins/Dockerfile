# Stage 1: Build
FROM python:3.11-alpine AS builder

WORKDIR /two_coins

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache build-base libffi-dev

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Production
FROM python:3.11-alpine

WORKDIR /two_coins

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache postgresql-client

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY . .

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
