FROM --platform=linux/amd64 python:3.12.13-slim-bookworm@sha256:6e13e65c55e33adf203d77ee371cf8bf5d81bd4902ef07565721f46bf44917af AS build

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_ONLY_BINARY=:all:
WORKDIR /build

COPY requirements/lock-tools.txt requirements/runtime.txt ./requirements/
RUN python -m ensurepip --upgrade \
    && python -m pip install --require-hashes --only-binary=:all: --no-deps -r requirements/lock-tools.txt \
    && python -m pip install --require-hashes --only-binary=:all: --no-deps -r requirements/runtime.txt

COPY pyproject.toml ./
COPY config ./config
COPY modules ./modules
RUN python -m pip wheel --no-build-isolation --no-deps --wheel-dir /wheels .

FROM --platform=linux/amd64 python:3.12.13-slim-bookworm@sha256:6e13e65c55e33adf203d77ee371cf8bf5d81bd4902ef07565721f46bf44917af AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_ONLY_BINARY=:all:
WORKDIR /app

RUN addgroup --system codesho && adduser --system --ingroup codesho codesho
COPY --from=build /build/requirements/runtime.txt /tmp/runtime.txt
COPY --from=build /wheels /tmp/wheels
COPY --chown=codesho:codesho manage.py /app/manage.py
RUN python -m pip install --require-hashes --only-binary=:all: --no-deps -r /tmp/runtime.txt \
    && python -m pip install --no-deps /tmp/wheels/*.whl \
    && python -m pip check \
    && rm -rf /tmp/runtime.txt /tmp/wheels \
              /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.* \
              /usr/local/lib/python3.12/site-packages/pip \
              /usr/local/lib/python3.12/site-packages/pip-*.dist-info \
              /usr/local/lib/python3.12/site-packages/setuptools \
              /usr/local/lib/python3.12/site-packages/setuptools-*.dist-info \
              /usr/local/lib/python3.12/site-packages/wheel \
              /usr/local/lib/python3.12/site-packages/wheel-*.dist-info \
              /usr/local/lib/python3.12/site-packages/build \
              /usr/local/lib/python3.12/site-packages/build-*.dist-info \
              /usr/local/lib/python3.12/ensurepip
COPY --chown=codesho:codesho config ./config
COPY --chown=codesho:codesho modules ./modules
USER codesho

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "60"]
