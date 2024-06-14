# Используем официальный образ MySQL с Docker Hub
FROM mysql:latest

# Необязательные параметры: укажите пользователя, пароль и название базы данных
ENV MYSQL_ROOT_PASSWORD=P@$$w0rd
ENV MYSQL_DATABASE=match_db
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=P@$$w0rd

# Копируем SQL скрипт инициализации (если он нужен)
COPY init.sql /docker-entrypoint-initdb.d/

# Опционально: укажите порт, который будет открыт в контейнере
EXPOSE 3306
