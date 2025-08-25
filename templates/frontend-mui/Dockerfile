FROM node:18-alpine

WORKDIR /app

# Copy package.json first (NOT package-lock.json yet)
COPY package.json ./

# ALWAYS do fresh install in Docker to ensure all dependencies are present
# This is more reliable than npm ci which can fail silently
RUN npm install --legacy-peer-deps && \
    # Explicitly verify critical dependencies are installed
    npm ls --depth=0 @mui/material @mui/icons-material @emotion/react @emotion/styled || \
    (echo "ERROR: Failed to install MUI dependencies" && exit 1)

# Now copy the rest of the application
COPY . .

EXPOSE 3000

CMD ["npm", "start"]