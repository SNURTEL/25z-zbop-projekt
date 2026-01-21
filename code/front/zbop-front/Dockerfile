# Development/Production stage
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Set environment variable for API URL (can be overridden at runtime)
ENV REACT_APP_API_URL=http://localhost:8000

# Start the application
CMD ["npm", "start"]
