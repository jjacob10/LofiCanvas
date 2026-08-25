FROM node:20-slim

# Install Python 3
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY package*.json ./
RUN npm install ws

COPY . .

# Expose Node.js frontend/gateway port
EXPOSE 3000

# Start both Python and Node concurrently
CMD python3 analyzer.py & node server.js