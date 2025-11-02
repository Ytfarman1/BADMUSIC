FROM nikolaik/python-nodejs:python3.10-nodejs19

# Switch Debian repositories to bullseye (current stable)
RUN sed -i 's/buster/bullseye/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg aria2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip3 install --no-cache-dir -U pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "-m", "BADMUSIC"]
CMD python3 -m BADMUSIC
