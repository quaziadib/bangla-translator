# Stage 1: Build React app
FROM node:20 AS build

ENV REACT_APP_API_BASE=http://localhost:8000

WORKDIR /home/quazi/Desktop/OfficeWorkRoot/app

COPY . .

RUN npm install
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/build /usr/share/nginx/html

# Copy default nginx config (optional override)
COPY nginx.conf /etc/nginx/conf.d/default.conf


EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
