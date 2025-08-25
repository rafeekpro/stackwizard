FROM node:18-alpine

WORKDIR /app

# Copy package.json first (NOT package-lock.json yet)
COPY package.json ./

# ALWAYS do fresh install in Docker to ensure all dependencies are present
# This is more reliable than npm ci which can fail silently
RUN npm install --legacy-peer-deps && \
    # Explicitly verify critical dependencies are installed
    npm ls @headlessui/react @heroicons/react tailwindcss || \
    (echo "ERROR: Failed to install Tailwind dependencies" && exit 1)

# Now copy the rest of the application
COPY . .

EXPOSE 3000

CMD ["npm", "start"]