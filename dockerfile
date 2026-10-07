FROM python:3.13-slim AS builder
WORKDIR /app

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

COPY facts_service ./facts_service
COPY rag_service ./rag_service
COPY ask_reponse_service ./ask_reponse_service

EXPOSE 8000 8001

# Default app; override per service in docker-compose.yaml
CMD ["uvicorn", "facts_service.facts_controller:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
