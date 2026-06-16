# HyperProbe PoC — single-process target + agent (ARCHITECTURE_V2 §5.12)
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Runtime deps only — pytest stays in requirements-dev.txt for CI/local
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent/ agent/
COPY target/ target/
COPY breakpoints.yaml .
RUN mkdir -p snapshots

EXPOSE 8080 9090

ENTRYPOINT ["python", "-m", "agent.bootstrap"]
