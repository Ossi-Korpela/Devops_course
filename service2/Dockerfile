FROM node:14
WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install
COPY service2.js ./

CMD [ "node", "service2.js" ]
