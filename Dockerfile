#FROM python:3.5-alpine3.8
FROM python:3.5-stretch

#RUN apk add --no-cache wine xvfb
#RUN apt-get update && apt-get install -y \
  #wine \
  #xvfb
RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y wine32 xvfb

COPY ./winebin/winetricks /usr/local/bin/winetricks
COPY ./winebin/xvfb-run /usr/local/bin/xvfb-run

RUN chmod 0755 /usr/local/bin/xvfb-run

# Wine really doesn't like to be run as root, so let's set up a non-root
# environment
RUN adduser --system --home /home/wix wix
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
