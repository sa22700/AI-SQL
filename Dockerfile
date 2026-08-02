FROM nvidia/cuda:12.5.0-devel-ubuntu22.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-dev \
        python3-pip \
        build-essential \
        cmake \
        ninja-build \
        git \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install \
    --no-cache-dir \
    --upgrade \
    pip \
    setuptools \
    wheel

COPY requirements.txt .

RUN python3 -m pip install \
    --no-cache-dir \
    -r requirements.txt

RUN python3 -m pip uninstall \
    -y \
    llama-cpp-python \
    || true

RUN CMAKE_ARGS="-DGGML_CUDA=on" \
    FORCE_CMAKE=1 \
    python3 -m pip install \
        --no-cache-dir \
        --no-binary=llama-cpp-python \
        llama-cpp-python==0.3.14

COPY backend ./backend
COPY core ./core
COPY ui ./ui
COPY Main.py .

EXPOSE 8000

CMD [
    "python3",
    "-m",
    "uvicorn",
    "backend.Backsys:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]