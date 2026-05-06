FROM node:20-alpine AS builder
WORKDIR /app
COPY webapp/package*.json ./
RUN npm ci --omit=dev
COPY webapp/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY OpenClawBox/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]