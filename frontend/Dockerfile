# Frontend Dockerfile - Multi-stage build for production
FROM node:18-alpine as builder

WORKDIR /app

# API URL is injected at build time from the pipeline
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend code
COPY . .

# Build for production
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run production build
RUN npm install -g serve

# Copy built assets from builder
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3000

# Serve production build
CMD ["serve", "-s", "dist", "-l", "3000"]
