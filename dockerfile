FROM python:3.13-slim AS builder
WORKDIR /app

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

# image for production
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Keep the same folder layout as in the repo so Python package imports work.
COPY database ./database
COPY rag_service ./rag_service

EXPOSE 8000

CMD ["uvicorn", "database.facts_controller:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
