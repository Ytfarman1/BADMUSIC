FROM nikolaik/python-nodejs:python3.10-nodejs19

# 🔧 Fix broken Debian repos and add missing GPG keys
RUN set -ex && \
    echo "deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends gnupg ca-certificates ffmpeg aria2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# 📦 Install Python deps
RUN pip3 install --no-cache-dir -U pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# 🚀 Start your bot
CMD ["python3", "-m", "BADMUSIC"]
