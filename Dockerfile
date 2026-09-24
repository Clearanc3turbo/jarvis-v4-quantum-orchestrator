FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY jarvis ./jarvis
COPY jarvis_launch.py jarvis_v5.py jarvis_vqc_layer.py ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
USER 10001:10001
ENTRYPOINT ["python", "jarvis_launch.py"]
