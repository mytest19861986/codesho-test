FROM --platform=linux/amd64 python:3.12.13-slim-bookworm@sha256:6e13e65c55e33adf203d77ee371cf8bf5d81bd4902ef07565721f46bf44917af AS build

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_ONLY_BINARY=:all:
WORKDIR /build

COPY requirements/lock-tools.txt requirements/runtime.txt ./requirements/
RUN python -m ensurepip --upgrade \
    && python -m pip install --require-hashes --no-deps -r requirements/lock-tools.txt \
    && python -m pip install --require-hashes --no-deps -r requirements/runtime.txt

COPY pyproject.toml ./
COPY config ./config
COPY modules ./modules
RUN python -m pip wheel --no-build-isolation --no-deps --wheel-dir /wheels .

FROM --platform=linux/amd64 python:3.12.13-slim-bookworm@sha256:6e13e65c55e33adf203d77ee371cf8bf5d81bd4902ef07565721f46bf44917af AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_ONLY_BINARY=:all: PATH=/venv/bin:$PATH
WORKDIR /app

RUN addgroup --system codesho && adduser --system --ingroup codesho codesho \
    && python -m venv /venv
COPY --from=build /build/requirements/runtime.txt /tmp/runtime.txt
COPY --from=build /wheels /tmp/wheels
COPY --chown=codesho:codesho manage.py /app/manage.py
RUN /venv/bin/python -m pip install --require-hashes --no-deps -r /tmp/runtime.txt \
    && /venv/bin/python -m pip install --no-deps /tmp/wheels/*.whl \
    && /venv/bin/python -m pip check \
    && /venv/bin/python -m pip uninstall --yes pip setuptools wheel \
    && rm -rf /tmp/runtime.txt /tmp/wheels
USER codesho

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "60"]
