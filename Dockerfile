FROM hyperspacetech/code-py-base:3.9-poetry1.2.1

WORKDIR /app/home

# To improve layers cache hit rate, install dependencies first, because this part is relative stable.
COPY pyproject.toml \
     poetry.lock \
     ./

# `--with dev` means "install the dev dependencies"
# `--no-root` means "install all dependencies but not the project(the app)
RUN poetry install --no-interaction --no-root --with dev && rm -rf /root/.cache/pypoetry

# Activate the virtualenv.
ENV PATH "/app/home/.venv/bin:$PATH"

# Install the app
ADD botchan ./botchan
RUN poetry install --no-interaction --with dev

# Misc stuff
ADD .pylintrc ./.pylintrc
ADD ./bin /app/bin/