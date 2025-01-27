FROM node:14
WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install
COPY gateway.js ./

CMD [ "node", "gateway.js" ]