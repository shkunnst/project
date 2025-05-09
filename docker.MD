# Шпаргалка: Подключение к сервису в Docker

## 1. **Подключение с хоста (локальной машины)**

Если сервис запущен в Docker, и вы хотите подключиться к нему с вашего локального компьютера, необходимо **пробросить порты** в `docker-compose.yml`.

### Пример:
```yaml
services:
  kafka:
    image: bitnami/kafka:latest
    ports:
      - "9092:9092"  # Пробрасываем порт 9092 контейнера на порт 9092 хоста
```

- **Как подключиться:**  
  Используйте `localhost:9092` в вашем коде или приложении.

---

## 2. **Подключение из другого контейнера**

Если ваш код или приложение также запущены в Docker, и вы хотите подключиться к сервису из другого контейнера, используйте **имя сервиса** (указанное в `docker-compose.yml`) и порт сервиса.

### Пример:
```yaml
services:
  kafka:
    image: bitnami/kafka:latest
    ports:
      - "9092:9092"  # Проброс порта для доступа с хоста
    networks:
      - my-network

  app:
    image: my-python-app
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092  # Подключение к Kafka по имени сервиса
    networks:
      - my-network
    depends_on:
      - kafka

networks:
  my-network:
    driver: bridge
```

- **Как подключиться:**  
  Используйте `kafka:9092` в вашем коде или приложении.

---

## 3. **Когда пробрасывать порты не нужно**

Если ваш код и сервис находятся в одной Docker-сети, пробрасывать порты на хост **не обязательно**. Достаточно использовать имя сервиса и порт.

### Пример:
```yaml
services:
  kafka:
    image: bitnami/kafka:latest
    networks:
      - my-network

  app:
    image: my-python-app
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092  # Подключение к Kafka по имени сервиса
    networks:
      - my-network
    depends_on:
      - kafka

networks:
  my-network:
    driver: bridge
```

- **Как подключиться:**  
  Используйте `kafka:9092` в вашем коде или приложении.

---

## 4. **Основные правила**

- **Для доступа с хоста:**  
  Пробрасывайте порты с помощью `ports` в `docker-compose.yml` и используйте `localhost:<порт>`.

- **Для доступа из другого контейнера:**  
  Используйте имя сервиса и порт (например, `kafka:9092`). Убедитесь, что оба контейнера находятся в одной сети.

- **Сети Docker:**  
  Если контейнеры находятся в одной сети, они могут общаться друг с другом по именам сервисов.

---

## 5. **Пример команды для проверки подключения**

- **С хоста:**  
  ```bash
  nc -zv localhost 9092
  ```

- **Из контейнера:**  
  ```bash
  docker exec -it <container_id> nc -zv kafka 9092
  ```

---

Теперь вы знаете, как правильно подключаться к сервисам в Docker! 🐳
Если все же есть необходимость подключиться извне (не используя докер), то необходимо 
1) пробросить порты как показано выше
2) изменить настройки kafka в docker compose файле:
- KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka1:9092 на
- KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
кажется кафка не хочет запускаться с такими настройками, я воспользовался командой - 
```bash
  docker run -d --name=kafka -p 9092:9092 apache/kafka
```

Это может понадобиться
```bash
mkdir -p ~/kafka-data
sudo chown -R 1001:1001 ~/kafka-data
```