ARG BUILD_FROM
FROM $BUILD_FROM AS base

WORKDIR /app

RUN apk add --no-cache nodejs npm

COPY package* /app/

FROM base AS builder

RUN npm ci

COPY ./src /app/src/
COPY tsconfig.json /app/tsconfig.json

RUN npm run build

FROM base

RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont

RUN npm ci --production

COPY --from=builder /app/dist /app/dist/
COPY ./entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
