ARG PYTHON_BASE=3.11-slim

FROM python:$PYTHON_BASE AS builder

RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false

WORKDIR /usr/src/app

COPY pyproject.toml ./
COPY pdm.lock ./

RUN pdm install
RUN pdm run chainlit init

FROM python:$PYTHON_BASE

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/.venv/ ./.venv
COPY --from=builder /usr/src/app/.chainlit/ ./.chainlit

ENV VIRTUALENV "/usr/src/app/.venv"
ENV PATH "$VIRTUALENV/bin:$PATH"

COPY app ./app

EXPOSE 8000

CMD ["uvcorn", "app:api", "--host", "0.0.0.0", "--port", "8000"]
