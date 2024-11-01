FROM python:3.11-slim

WORKDIR /app/home

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Add the bot-chan application
ADD botchan ./botchan

# Miscellaneous additions
ADD tests ./tests
ADD ./bin /app/bin/
ADD setup.py ./setup.py

# Install the app
RUN pip install -e .