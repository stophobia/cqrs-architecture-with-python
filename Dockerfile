FROM python:3.12-slim

# Set environment variables early
ENV LANG=pt_BR.UTF-8 \
    LANGUAGE=pt_BR:pt_br \
    LC_ALL=pt_BR.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/home/userapp/app/src/

# Create user
RUN useradd -m -s /bin/bash userapp

# Install dependencies and clean up
RUN apt update && apt install -y --no-install-recommends \
        make \
        ca-certificates \
        locales \
        build-essential \
    && update-ca-certificates \
    && locale-gen pt_BR.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /home/userapp/app

# Upgrade pip and install Poetry
RUN python -m ensurepip --upgrade \
    && pip install --no-cache-dir --upgrade pip poetry \
    && poetry config virtualenvs.create false

# Copy Poetry files and install dependencies
COPY --chown=userapp:userapp pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-cache -vvv

# Copy remaining app source
COPY --chown=userapp:userapp . .

# Switch to app user
USER userapp

# Entrypoint and command
ENTRYPOINT ["poetry", "run", "--"]
CMD ["./start.sh"]
