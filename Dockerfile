FROM python:3.10.10

ENV POETRY_VERSION=2.0.0
RUN pip3 install poetry==$POETRY_VERSION

WORKDIR /var/project

COPY ./pyproject.toml ./
COPY ./poetry.lock ./

ARG PIP_TOKEN
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./ ./

ENV PYTHONPATH = ${PYTHONPATH}:/var/project:/var/project/app
WORKDIR /var/project/app

ARG MAX_WORKERS
RUN echo "uvicorn --static-path-mount /var/project/app/static --log-level debug --interface asgi --access-log --host 0.0.0.0 --port \${PORT} --workers ${MAX_WORKERS} --respawn-failed-workers --access-log main:app" > /run_module.sh

ENTRYPOINT ["python", "run.py"]
