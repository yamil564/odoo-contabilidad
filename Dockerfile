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
            python3-defusedxml \
        && pip3 install --upgrade setuptools  pip \
        && pip3 install cryptography \
            ipaddress \
            signxml \
            openpyxl

RUN apt-get -y install locales locales-all
RUN update-locale 


RUN apt-get install -y poppler-utils 
RUN python3 -m pip install --upgrade pip
RUN apt-get clean && apt-get autoclean
RUN pip3 install pyjwt
RUN pip3 install phonenumbers
RUN pip3 install boto3
RUN pip3 install lxml
RUN pip3 install flex
RUN pip3 install pandas
RUN pip3 install numpy
RUN pip3 install simplejson
RUN pip3 install paramiko
RUN apt-get install -y libmagic-dev
RUN pip3 install --user libmagic
RUN pip install culqi
RUN pip install mercadopago
RUN pip3 install facebook-sdk
RUN pip3 install pillow
RUN pip3 install html2text
RUN pip install wheel 
RUN pip install cerberus 
RUN pip install pyquerystring 
RUN pip install parse-accept-language 
RUN pip install apispec 
RUN pip install cachetools 
RUN pip install marshmallow 
RUN pip install marshmallow_objects 
RUN pip install jsondiff
RUN pip install extendable-pydantic
RUN apt-get clean && apt-get autoclean
RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
RUN pip3 install pdf2image