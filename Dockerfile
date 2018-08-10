FROM python:3.5-alpine3.8

RUN apk update
RUN apk add wine xvfb

COPY ./winebin/winetricks /usr/local/bin/winetricks
COPY ./winebin/xvfb-run /usr/local/bin/xvfb-run

# Prefix commands passed into bash so that they run in xvfb
ENTRYPOINT xvfb-run -a wine


RUN apk add wget

# Wine really doesn't like to be run as root, so let's set up a non-root
# environment

RUN adduser -S -h /home/wix wix
USER wix
ENV HOME /home/wix
ENV WINEPREFIX /home/wix/.wine
ENV WINEARCH win32

# Install .NET Framework 4.0
RUN wine wineboot && xvfb-run winetricks --unattended dotnet40 corefonts

# Install WiX
RUN mkdir /home/wix/wix
WORKDIR /home/wix/wix
ADD wix38-binaries.zip /home/wix/wix/wix38-binaries.zip
RUN unzip /home/wix/wix/wix38-binaries.zip
RUN rm /home/wix/wix/wix38-binaries.zip
