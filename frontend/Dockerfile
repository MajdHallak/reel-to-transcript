# Build Stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production Stage (Nginx)
FROM nginx:alpine
# Copy the compiled React build into the Nginx server
COPY --from=builder /app/dist /usr/share/nginx/html
# Expose standard web port
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]