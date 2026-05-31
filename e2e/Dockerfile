FROM mcr.microsoft.com/playwright:v1.51.0-jammy

WORKDIR /e2e

COPY package.json package-lock.json ./
RUN npm ci

COPY playwright.config.js ./
COPY fixtures ./fixtures
COPY tests ./tests

ENV E2E_DOCKER=1
ENV BASE_URL=http://frontend:3000

CMD ["npx", "playwright", "test"]
