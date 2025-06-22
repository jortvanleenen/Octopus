FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake g++ gcc git curl gpg pkg-config \
    libboost-all-dev libgc-dev bison flex graphviz \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone --depth=1 --recurse-submodules https://github.com/p4lang/p4c.git && \
    cd p4c && \
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
    && make -j$(nproc) && make install && \
    cd / && rm -rf /build

COPY . /octopus
WORKDIR /octopus

RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir hatch && \
    pip install --no-cache-dir -e .[dev] && \
    python3 -m pysmt install --z3 --cvc5 --confirm-agreement && \
    python3 -m pysmt install --check

ENTRYPOINT ["octopus"]
