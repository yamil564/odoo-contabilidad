FROM odoo:13.0

LABEL MAINTAINER Daniel Moreno <danielvdmlfiis@gmail.com>
USER root


RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends python3-dev\
            build-essential \
            gcc \
            python3-cffi \
            libxml2-dev \
            libxslt1-dev \
            libssl-dev \
            python3-lxml \
            python3-cryptography \
            python3-openssl  \
            python3-defusedxml \
        && pip3 install --upgrade setuptools  pip \
        && pip3 install cryptography \
            ipaddress \
            signxml 

RUN apt-get clean && apt-get autoclean

RUN pip3 install phonenumbers


RUN pip3 install boto3
RUN pip3 install lxml
RUN pip3 install flex
RUN pip3 install pandas
RUN pip3 install numpy
RUN apt-get install -y libmagic-dev
RUN pip3 install --user libmagic