FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

RUN npm cache clean --force && \
    find node_modules -type f -name "vite" -exec chmod +x {} \; || true

CMD ["npx", "vite", "--host", "0.0.0.0", "--port", "5173"]
