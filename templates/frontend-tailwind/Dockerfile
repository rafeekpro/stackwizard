FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with clean install to ensure lock file is respected
RUN npm ci || npm install

# Copy application files
COPY . .

EXPOSE 3000

CMD ["npm", "start"]