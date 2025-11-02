FROM nikolaik/python-nodejs:python3.10-nodejs19

# Fix outdated Debian repositories & add missing GPG keys
RUN apt-get update || true && \
    apt-get install -y --no-install-recommends gnupg ca-certificates && \
    sed -i 's|buster|bookworm|g' /etc/apt/sources.list && \
    sed -i 's|bullseye|bookworm|g' /etc/apt/sources.list && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6ED0E7B82643E131 78DBA3BC47EF2265 F8D2585B8783D481 || true && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg aria2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install requirements
RUN pip3 install --no-cache-dir -U pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# Start your bot
CMD ["python3", "-m", "BADMUSIC"]
