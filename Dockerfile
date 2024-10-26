FROM python:3.11-slim

WORKDIR /app/home

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Add the bot-chan application
ADD botchan ./botchan

# Miscellaneous additions
ADD tests ./tests
ADD .pylintrc ./.pylintrc
ADD ./bin /app/bin/
