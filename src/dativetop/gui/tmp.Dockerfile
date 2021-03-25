FROM node:13.3.0

RUN apt-get update && apt-get -q -y install \
      openjdk-8-jdk \
      curl \
    && curl -s https://download.clojure.org/install/linux-install-1.10.1.492.sh | bash \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g shadow-cljs

RUN npx shadow-cljs release dativetop-gui
