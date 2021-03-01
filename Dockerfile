FROM odoo:13.0

LABEL MAINTAINER Daniel Moreno <danielvdmlfiis@gmail.com>
USER root

RUN pip3 install pyjwt
# RUN set -x; \
#         apt-get update \
#         && apt-get install -y --no-install-recommends python-dev\
#             build-essential \
#             gcc \
#             tesseract-ocr-eng \
#             tesseract-ocr\
#             libtesseract-dev\
#             python-pil\
#             python-bs4 

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

# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils
# RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb --output google-chrome-stable_current_amd64.deb
# RUN dpkg -i google-chrome-stable_current_amd64.deb ; apt-get -fy install
# RUN apt install --assume-yes chromium-browser
RUN pip3 install phonenumbers
RUN pip3 install selenium

# RUN pip3 install pillow
# RUN pip3 install tesseract
# RUN pip3 install pytesseract
# RUN pip3 install beautifulsoup4
RUN pip3 install boto3
RUN pip3 install lxml
RUN pip3 install flex
RUN pip3 install pynamodb
# RUN pip3 install culqipy
# RUN pip3 install mercadopago
# RUN apt-get clean && apt-get autoclean

