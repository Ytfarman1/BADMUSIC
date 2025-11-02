FROM nikolaik/python-nodejs:python3.10-nodejs19

# 🧩 Fix Debian source list & install ffmpeg/aria2 safely (no version conflict)
RUN set -ex && \
    sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/99no-check-valid && \
    apt-get -o Acquire::ForceIPv4=true update && \
    apt-get install -y --no-install-recommends ffmpeg aria2 ca-certificates gnupg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# 🐍 Python dependencies
RUN pip3 install --no-cache-dir -U pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# 🚀 Start bot
CMD python3 -m BADMUSIC & python3 web.py
