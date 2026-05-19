FROM js_image

WORKDIR /app

# Копируем весь код
COPY . .

# Открываем порт для React dev сервера
EXPOSE 3000

# Запускаем React в режиме разработки
CMD ["npm", "start"]