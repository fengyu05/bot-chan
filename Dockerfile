FROM hyperspacetech/code-py-base:3.9-poetry1.2.1

WORKDIR /app/py/projects/botchan

# To improve layers cache hit rate, install dependencies first, because this part is relative stable.
COPY pyproject.toml \
     poetry.lock \
     ./
# `--no-root` means "install all dependencies but not the project
RUN poetry install --no-interaction --no-root && rm -rf /root/.cache/pypoetry

# Activate the virtualenv.
ENV PATH "/app/py/projects/botchan/.venv/bin:$PATH"

# Install the app
ADD botchan ./botchan
RUN poetry install --no-interaction

# Misc stuff
ADD .pylintrc ./.pylintrc