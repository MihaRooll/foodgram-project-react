# Используйте базовый образ Node.js для сборки фронтенда
FROM node:13.12.0-alpine as build

# Установка зависимостей и сборка фронтенда
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build

# Копирование собранного фронтенда в отдельную директорию
CMD cp -r build result_build
