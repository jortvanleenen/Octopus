FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl gpg apt-transport-https ca-certificates python3.10 python3-pip && \
    echo 'deb https://download.opensuse.org/repositories/home:/p4lang/xUbuntu_22.04/ /' > /etc/apt/sources.list.d/home_p4lang.list && \
    curl -fsSL https://download.opensuse.org/repositories/home:/p4lang/xUbuntu_22.04/Release.key | gpg --dearmor > /etc/apt/trusted.gpg.d/home_p4lang.gpg && \
    apt-get update && \
    apt-get install -y p4lang-p4c && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /octopus
WORKDIR /octopus

RUN pip install --upgrade pip \
    && pip install hatch \
    && pip install -e .[dev]

RUN python3 -m pysmt install --z3 --cvc5 --confirm-agreement \
    && python3 -m pysmt install --check

ENTRYPOINT ["octopus"]
