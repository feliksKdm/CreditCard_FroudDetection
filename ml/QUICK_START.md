# 🚀 Быстрый Справочник - Развертывание на AWS EC2

## Что было создано

Полная Flask система для развертывания модели обнаружения мошенничества:

| Файл | Назначение |
|------|-----------|
| `main.py` | Основное Flask приложение с API endpoints |
| `requirements.txt` | Python зависимости |
| `client_example.py` | Python клиент для использования API |
| `README.md` | Полная документация проекта |
| `AWS_DEPLOYMENT.md` | Подробное руководство по развертыванию |
| `deploy.sh` | Автоматический скрипт установки на EC2 |
| `Dockerfile` | Docker конфигурация для контейнеризации |
| `docker-compose.yml` | Docker Compose конфигурация |
| `test_api.sh` | Тестовый скрипт для проверки API |
| `.gitignore` | Исключения для Git |

---

## ⚡ Быстрый старт

### 1️⃣ Локальное тестирование (5 мин)

```bash
# Создать окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python main.py

# В другом терминале, тестировать
curl http://localhost:5000/health
```

### 2️⃣ Развертывание на AWS EC2 (15 мин)

```bash
# Шаг 1: Запустить Ubuntu EC2 инстанс
# - t2.medium или выше
# - Открыть порты 22 и 5000

# Шаг 2: Загрузить файлы на EC2
scp -i key.pem -r /path/to/FroudDet_AWS ubuntu@YOUR_EC2_IP:~/

# Шаг 3: Подключиться и запустить развертывание
ssh -i key.pem ubuntu@YOUR_EC2_IP
cd FroudDet_AWS
chmod +x deploy.sh
./deploy.sh

# Шаг 4: Загрузить модель
# На локальной машине:
scp -i key.pem voting_classifier_model.pkl ubuntu@YOUR_EC2_IP:~/FroudDet_AWS/

# Шаг 5: Запустить сервис
ssh -i key.pem ubuntu@YOUR_EC2_IP
sudo systemctl start fraud-detection
sudo systemctl status fraud-detection
```

### 3️⃣ Docker развертывание (10 мин)

```bash
# На EC2:
ssh -i key.pem ubuntu@YOUR_EC2_IP
cd FroudDet_AWS

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Запустить контейнер
docker-compose up -d

# Проверить статус
docker-compose logs -f
```

---

## 📊 API Endpoints

### Запросы с примерами

```bash
# 1. Проверка здоровья
curl http://YOUR_EC2_IP:5000/health

# 2. Одиночное предсказание
curl -X POST http://YOUR_EC2_IP:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "oldbalanceOrig": 5000,
    "newbalanceOrig": 4000,
    "oldbalanceDest": 100,
    "newbalanceDest": 1100,
    "type": "PAYMENT"
  }'

# 3. Пакетное предсказание (несколько сразу)
curl -X POST http://YOUR_EC2_IP:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {...}, 
      {...}
    ]
  }'
```

---

## 🧪 Тестирование

### Полный набор тестов

```bash
# Локально
./test_api.sh http://localhost:5000

# На EC2
./test_api.sh http://YOUR_EC2_IP:5000
```

### Python клиент

```python
from client_example import FraudDetectionClient

client = FraudDetectionClient('http://YOUR_EC2_IP:5000')
result = client.predict({
    "amount": 1000,
    "oldbalanceOrig": 5000,
    "newbalanceOrig": 4000,
    "oldbalanceDest": 100,
    "newbalanceDest": 1100,
    "type": "PAYMENT"
})
print(f"Is Fraud: {result['is_fraud']}")
print(f"Confidence: {result['fraud_probability']:.4f}")
```

---

## 🔍 Входные параметры модели

```json
{
  "amount": 1000.0,                    // Сумма транзакции
  "oldbalanceOrig": 5000.0,            // Исходный баланс отправителя
  "newbalanceOrig": 4000.0,            // Новый баланс отправителя
  "oldbalanceDest": 100.0,             // Исходный баланс получателя
  "newbalanceDest": 1100.0,            // Новый баланс получателя
  "type": "PAYMENT"                    // Тип: CASH_IN, PAYMENT, CASH_OUT, TRANSFER, DEBIT
}
```

---

## 📈 Ответ модели

```json
{
  "prediction": 0,                      // 0 = Легитимно, 1 = Мошенничество
  "fraud_probability": 0.0234,          // Вероятность мошенничества
  "legitimate_probability": 0.9766,     // Вероятность легитимности
  "is_fraud": false                     // Boolean результат
}
```

---

## 🛠️ Управление на EC2

```bash
# Запустить сервис
sudo systemctl start fraud-detection

# Остановить сервис
sudo systemctl stop fraud-detection

# Перезагрузить конфигурацию
sudo systemctl restart fraud-detection

# Статус сервиса
sudo systemctl status fraud-detection

# Просмотр логов
sudo journalctl -u fraud-detection -f

# Автозапуск при перезагрузке
sudo systemctl enable fraud-detection
```

---

## 🐳 Docker команды

```bash
# Запустить контейнер
docker-compose up -d

# Остановить контейнер
docker-compose down

# Просмотр логов
docker-compose logs -f

# Статус контейнера
docker-compose ps

# Перестроить образ
docker-compose build --no-cache

# Очистить всё
docker-compose down -v
```

---

## 📊 Параметры запуска Gunicorn

Для изменения производительности в `deploy.sh` или `docker-compose.yml`:

```bash
# Больше workers (для высокой нагрузки)
gunicorn --workers 8 --bind 0.0.0.0:5000 main:app

# Меньше workers (для ограниченной памяти)
gunicorn --workers 2 --bind 0.0.0.0:5000 main:app

# С timeout и retry
gunicorn --workers 4 --timeout 120 --bind 0.0.0.0:5000 main:app
```

---

## ⚠️ Типичные проблемы

| Проблема | Решение |
|---------|---------|
| Port 5000 занят | `lsof -i :5000` и `kill -9 <PID>` |
| Модель не загружается | Проверить `voting_classifier_model.pkl` существует |
| Недостаточно памяти | Уменьшить workers: `--workers 2` |
| API не отвечает | Проверить Security Group открыт порт 5000 |
| Service не стартует | Посмотреть логи: `sudo journalctl -u fraud-detection` |

---

## 🔐 Prodакшн Рекомендации

1. **SSL/HTTPS**: Используйте Let's Encrypt для бесплатного сертификата
2. **Nginx**: Используйте как reverse proxy для безопасности
3. **Security Group**: Ограничьте доступ только необходимым IP
4. **Мониторинг**: Настройте CloudWatch для мониторинга
5. **Backup**: Регулярно создавайте снимки EC2 инстанса

---

## 📚 Полная документация

- Подробное руководство: [`AWS_DEPLOYMENT.md`](AWS_DEPLOYMENT.md)
- Общая документация: [`README.md`](README.md)
- Примеры кода: [`client_example.py`](client_example.py)

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи приложения
2. Запустите тесты: `./test_api.sh`
3. Смотрите документацию в `AWS_DEPLOYMENT.md`
4. Проверьте Security Group и Network ACLs на AWS

---

**Версия**: 1.0  
**Дата создания**: 2026-05-06  
**Модель**: Voting Classifier (CatBoost + RandomForest + XGBoost)
