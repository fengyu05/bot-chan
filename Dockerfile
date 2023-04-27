FROM hyperspacetech/code-py-base:3.9-poetry1.2.1

WORKDIR /app/py/projects/botchan

# To improve layers cache hit rate, install dependencies first, because this part is relative stable.
COPY pyproject.toml \
     poetry.lock \
     ./
RUN poetry install && rm -rf /root/.cache/pypoetry

# Activate the virtualenv.
ENV PATH "/app/py/projects/botchan/.venv/bin:$PATH"

ADD botchan ./botchan

RUN poetry install
