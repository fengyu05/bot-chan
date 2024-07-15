FROM hyperspacetech/code-py-base:3.9-poetry1.2.1
# This Dockefile is for ci tool which doesn't need the app running
WORKDIR /app/home

COPY pyproject.toml \
     poetry.lock \
     .pylintrc \
     ./

# `--only dev` means only to install dev deps
RUN poetry install --no-interaction --only dev

# Activate the virtualenv.
ENV PATH "/app/home/.venv/bin:$PATH"