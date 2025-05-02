FROM ubuntu:22.04

# --- System deps ---
RUN apt update && apt install -y \
    build-essential \
    git \
    wget \
    curl \
    cmake \
    g++ \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    libboost-all-dev \
    samtools \
    jellyfish \
    bowtie2 \
    perl \
    python3.10 \
    python3-pip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# --- Trinity install ---
WORKDIR /opt
RUN git clone --recursive https://github.com/trinityrnaseq/trinityrnaseq.git
WORKDIR /opt/trinityrnaseq
RUN make && ln -s /opt/trinityrnaseq/Trinity /usr/local/bin/Trinity

# --- Project files ---
WORKDIR /app
COPY . /app
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# --- Environment prep ---
ENV PATH="/opt/trinityrnaseq:$PATH"
ENV TRINITY_NO_SALMON=1

# --- Start FastAPI ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
