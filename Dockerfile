FROM nikolaik/python-nodejs:python3.10-nodejs19

# 🧩 Fix Debian repo and disable problematic IPv6 sources
RUN set -ex && \
    sed -i 's|http://deb.debian.org|http://deb.debian.org|g' /etc/apt/sources.list || true && \
    echo "deb [arch=amd64] http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://security.debian.org bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    apt-get -o Acquire::ForceIPv4=true update && \
    apt-get install -y --no-install-recommends ffmpeg aria2 ca-certificates gnupg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# 🔧 Install dependencies safely
RUN pip3 install --no-cache-dir -U pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# 🚀 Launch the bot
CMD ["python3", "-m", "BADMUSIC"]
