FROM python:3.10-slim

# P4C (only p4c-graphs backend)
RUN apt-get update && apt-get install -y \
    cmake g++ curl gcc gpg git pkg-config \
    libboost-all-dev libgc-dev bison flex graphviz \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone --recursive https://github.com/p4lang/p4c.git /p4c && \
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

# Octopus
COPY . /octopus
WORKDIR /octopus

RUN pip install --upgrade pip && \
    pip install hatch && \
    pip install -e .[dev]

# Install SMT solvers for PySMT (Z3 and cvc5)
RUN python -m pysmt install --z3 --cvc5 --confirm-agreement && \
    python -m pysmt install --check

ENTRYPOINT ["octopus"]
