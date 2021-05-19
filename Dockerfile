FROM python:3.8-slim-buster

# Install cron
RUN apt-get update && apt-get -y install cron

# Set /app as working directory
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy application files
COPY krakenohlc/ krakenohlc/
COPY config.yaml config.yaml
COPY __main__.py __main__.py

# Create data output folder
RUN mkdir -p /app/data

CMD ["python3", "-u", "__main__.py"]