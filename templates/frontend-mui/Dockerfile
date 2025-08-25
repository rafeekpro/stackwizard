FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with fallback
# First try npm ci for faster, reproducible builds
# If that fails or package-lock.json is missing, use npm install
RUN if [ -f package-lock.json ]; then \
      npm ci || npm install; \
    else \
      npm install; \
    fi && \
    # Verify critical dependencies are installed
    npm ls @mui/material @mui/icons-material || npm install @mui/material @mui/icons-material @emotion/react @emotion/styled

# Copy application files
COPY . .

EXPOSE 3000

CMD ["npm", "start"]