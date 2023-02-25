FROM python:3.11-slim
RUN apt update && apt install git curl wget -y
RUN mkdir -p ~/bin
RUN wget https://github.com/casey/just/releases/download/1.13.0/just-1.13.0-x86_64-unknown-linux-musl.tar.gz &&\
    tar -xzf just-1.13.0-x86_64-unknown-linux-musl.tar.gz &&\
    mv just /bin/ &&\
    rm just-1.13.0-x86_64-unknown-linux-musl.tar.gz

RUN pip install poetry && poetry config virtualenvs.create false
RUN mkdir /app
WORKDIR /app
ENV PYTHONPATH=/app/:$PYTHONPATH
ADD poetry.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/pypoetry/artifacts \
    --mount=type=cache,target=/root/.cache/pypoetry/cache \
    poetry install
ADD . /app/