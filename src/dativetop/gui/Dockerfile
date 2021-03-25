FROM theasp/clojurescript-nodejs:shadow-cljs-alpine

WORKDIR /usr/src/app

COPY package.json ./package.json
COPY yarn.lock ./yarn.lock

RUN yarn

COPY assets ./assets
COPY shadow-cljs.edn ./shadow-cljs.edn
COPY src ./src

RUN mkdir -p target && cp assets/index.html target/

RUN npx shadow-cljs release dativetop-gui