FROM node:18-alpine

WORKDIR /app

# Copy package.json first (NOT package-lock.json yet)
COPY package.json ./

# ALWAYS do fresh install in Docker to ensure all dependencies are present
# This is more reliable than npm ci which can fail silently
RUN npm install --legacy-peer-deps && \
    # Explicitly verify critical dependencies are installed
    npm ls @headlessui/react @heroicons/react tailwindcss || \
    for pkg in @headlessui/react @heroicons/react tailwindcss; do \
        npm ls --depth=0 "$pkg" | grep "$pkg" > /dev/null || \
        (echo "ERROR: Failed to install $pkg" && exit 1); \
    done

# Now copy the rest of the application
COPY . .

EXPOSE 3000

CMD ["npm", "start"]