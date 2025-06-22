FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    curl gpg apt-transport-https ca-certificates \
    pkg-config libboost-all-dev libgc-dev bison flex graphviz \
    && echo 'deb https://download.opensuse.org/repositories/home:/p4lang/Debian_11/ /' \
         > /etc/apt/sources.list.d/home:p4lang.list \
    && curl -fsSL https://download.opensuse.org/repositories/home:/p4lang/Debian_11/Release.key \
         | gpg --dearmor \
         > /etc/apt/trusted.gpg.d/home_p4lang.gpg \
    && apt-get update \
    && apt-get install -y p4lang-p4c \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /octopus
WORKDIR /octopus

RUN pip install --upgrade pip \
    && pip install hatch \
    && pip install -e .[dev]

RUN python -m pysmt install --z3 --cvc5 --confirm-agreement \
    && python -m pysmt install --check

ENTRYPOINT ["octopus"]
