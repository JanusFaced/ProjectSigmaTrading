FROM node:20-alpine

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем весь код
COPY . .

# Открываем порт для React dev сервера
EXPOSE 3000

# Запускаем React в режиме разработки
CMD ["npm", "start"]