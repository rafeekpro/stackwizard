FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
# Install dependencies with clean install to ensure lock file is respected
RUN npm ci || npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]