FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN addgroup --system codesho && adduser --system --ingroup codesho codesho
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .
# The final image is a runtime image: remove package-management and build
# tooling from the system interpreter after installing the application.
RUN rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.* \
    && rm -rf /usr/local/lib/python3.12/site-packages/pip \
              /usr/local/lib/python3.12/site-packages/pip-*.dist-info \
              /usr/local/lib/python3.12/site-packages/build \
              /usr/local/lib/python3.12/site-packages/build-*.dist-info \
              /usr/local/lib/python3.12/ensurepip
COPY . .
RUN rm -rf /app/build
RUN chown -R codesho:codesho /app
USER codesho

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "60"]
