FROM python:3.10
 
ENV DEBIAN_FRONTEND noninteractive
ENV GECKODRIVER_VER v0.31.0
ENV FIREFOX_VER 87.0
WORKDIR /app

RUN set -x \
   && apt update \
   && apt upgrade -y \
   && apt install -y \
       wfrench \
       git \
       libx11-xcb1 \
       libdbus-glib-1-2 \
       libasound2 \
       libgtk-3-0 \
       xvfb \
       nano \
       tigervnc-standalone-server \
   && git clone https://github.com/piair338/MsRewards \
   && pip install -r MsRewards/requirements.txt \
   && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/91.9.1esr/linux-x86_64/en-US/firefox-91.9.1esr.tar.bz2 \
   && tar -jxf firefox-* \
   && mv firefox /opt/ \
   && chmod 755 /opt/firefox \
   && chmod 755 /opt/firefox/firefox \
   && ln -s /opt/firefox/firefox /usr/bin/firefox \
   && curl -sSLO https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz \
   && tar zxf geckodriver-*.tar.gz \
   && mv geckodriver /usr/bin/


WORKDIR /app/MsRewards
CMD python main.py

