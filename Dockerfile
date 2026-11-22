FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --no-create-home app

# Dependencies in a separate layer so code changes don't trigger a reinstall
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot ./bot

USER app

CMD ["python", "-m", "bot.main"]
