FROM nikolaik/python-nodejs:python3.10-nodejs19

# Fix outdated Debian sources (buster/bullseye → bookworm)
RUN sed -i 's|buster|bookworm|g' /etc/apt/sources.list && \
    sed -i 's|bullseye|bookworm|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg aria2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install requirements
RUN pip3 install --no-cache-dir -U pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python3", "-m", "BADMUSIC"]
