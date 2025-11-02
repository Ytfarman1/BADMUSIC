FROM nikolaik/python-nodejs:python3.10-nodejs19

# 🔧 Fix broken Debian GPG keys and force IPv4 to avoid 404 errors
RUN set -ex && \
    apt-get update || true && \
    apt-get install -y --no-install-recommends gnupg ca-certificates && \
    echo "deb [trusted=yes] http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb [trusted=yes] http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6ED0E7B82643E131 78DBA3BC47EF2265 F8D2585B8783D481 || true && \
    apt-get -o Acquire::ForceIPv4=true update && \
    apt-get install -y --no-install-recommends ffmpeg aria2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# 🐍 Install Python deps safely
RUN pip3 install --no-cache-dir -U pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# 🚀 Start bot
CMD ["python3", "-m", "BADMUSIC"]
