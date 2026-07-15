FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN addgroup --system codesho && adduser --system --ingroup codesho codesho
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .
COPY . .
RUN chown -R codesho:codesho /app
USER codesho

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "60"]
