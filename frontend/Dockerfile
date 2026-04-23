FROM node:20-alpine AS build
WORKDIR /app

# Use `npm ci` so the build is reproducible against the committed
# package-lock.json. `npm install` would silently resolve a newer
# transitive dependency and make builds non deterministic.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY index.html vite.config.js ./
COPY public/ ./public/
COPY src/ ./src/
RUN npm run build

FROM nginx:alpine

# wget is used by the compose level healthcheck; curl would pull in
# libcurl and grow the image for no benefit.
RUN apk add --no-cache wget

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/ >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]
