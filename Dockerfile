# syntax=docker/dockerfile:1
# Stage 1: Build p4c from source
FROM python:3.12-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    cmake g++ curl gcc gpg git pkg-config \
    libboost-all-dev libgc-dev bison flex graphviz

RUN git clone --depth=1 --recursive https://github.com/p4lang/p4c.git /p4c && \
    cd /p4c && \
    mkdir build && cd build && \
    cmake .. \
      -DENABLE_BMV2=OFF \
      -DENABLE_EBPF=OFF \
      -DENABLE_P4TC=OFF \
      -DENABLE_UBPF=OFF \
      -DENABLE_DPDK=OFF \
      -DENABLE_P4FMT=OFF \
      -DENABLE_P4TEST=OFF \
      -DENABLE_GTESTS=OFF \
    && make -j4 && make install

# Stage 2: Create final image
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /octopus

COPY --from=builder /usr/local /usr/local
COPY --from=builder /usr/lib/x86_64-linux-gnu/libboost_* /usr/lib/x86_64-linux-gnu/

RUN apt-get update && apt-get install -y --no-install-recommends cpp time

COPY . /octopus

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir hatch && \
    pip install --no-cache-dir -e .[dev] && \
    python3 -m pysmt install --cvc5 --confirm-agreement && \
    python3 -m pysmt install --check

ENTRYPOINT ["octopus"]
