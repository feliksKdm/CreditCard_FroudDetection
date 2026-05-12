# Fraud Detection Model API

Flask приложение для развертывания модели обнаружения мошенничества на AWS EC2.

## 📋 Содержание

- [Требования](#требования)
- [Локальное тестирование](#локальное-тестирование)
- [Развертывание на AWS EC2](#развертывание-на-aws-ec2)
- [API документация](#api-документация)
- [Примеры использования](#примеры-использования)
- [Мониторинг](#мониторинг)

## 🔧 Требования

### Для локального запуска:
- Python 3.8+
- pip
- 4GB+ оперативной памяти

### Для AWS EC2:
- Ubuntu Server 20.04 LTS или выше
- t2.medium инстанс или больше
- 20GB+ дискового пространства

## 🚀 Локальное тестирование

### 1. Установка зависимостей

```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать окружение
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Подготовка модели

Убедитесь, что файл `voting_classifier_model.pkl` находится в корневой папке проекта.

Если модель еще не создана, запустите ячейки в `test.ipynb`:

```bash
jupyter notebook test.ipynb
```

### 3. Запуск приложения

```bash
# Разработка (с debug режимом)
python main.py

# Продакшн (рекомендуется)
gunicorn --workers 4 --bind 127.0.0.1:5000 main:app
```

### 4. Тестирование API

```bash
# Проверка здоровья
curl http://localhost:5000/health

# Одиночное предсказание
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "oldbalanceOrig": 5000,
    "newbalanceOrig": 4000,
    "oldbalanceDest": 100,
    "newbalanceDest": 1100,
    "type": "PAYMENT"
  }'
```

## 🌐 Развертывание на AWS EC2

### Вариант 1: Автоматизированное развертывание

```bash
# 1. Загрузить скрипт на EC2
scp -i your_key.pem deploy.sh ubuntu@your_instance_ip:~/

# 2. Подключиться к EC2
ssh -i your_key.pem ubuntu@your_instance_ip

# 3. Выполнить скрипт
chmod +x deploy.sh
./deploy.sh

# 4. Загрузить файлы проекта
# На локальной машине:
scp -i your_key.pem main.py requirements.txt ubuntu@your_instance_ip:~/FroudDet_AWS/
scp -i your_key.pem voting_classifier_model.pkl ubuntu@your_instance_ip:~/FroudDet_AWS/

# 5. Запустить сервис
ssh -i your_key.pem ubuntu@your_instance_ip
sudo systemctl start fraud-detection
sudo systemctl enable fraud-detection
```

### Вариант 2: Docker развертывание

```bash
# 1. На локальной машине, подготовить файлы и загрузить
scp -i your_key.pem Dockerfile docker-compose.yml requirements.txt main.py voting_classifier_model.pkl ubuntu@your_instance_ip:~/FroudDet_AWS/

# 2. На EC2 инстансе, установить Docker
ssh -i your_key.pem ubuntu@your_instance_ip
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 3. Запустить контейнер
cd ~/FroudDet_AWS
docker-compose up -d

# 4. Проверить статус
docker-compose logs -f
```

### Вариант 3: Ручное развертывание

Смотрите полную документацию в файле `AWS_DEPLOYMENT.md`

## 📚 API Документация

### Endpoints

#### 1. GET `/`
Получить информацию об API и документацию

**Response:**
```json
{
  "app": "Fraud Detection Model API",
  "version": "1.0",
  "endpoints": {...}
}
```

#### 2. GET `/health`
Проверка здоровья приложения

**Response:**
```json
{
  "status": "healthy",
  "message": "Model loaded and ready"
}
```

#### 3. POST `/predict`
Одиночное предсказание

**Request:**
```json
{
  "amount": 1000.0,
  "oldbalanceOrig": 5000.0,
  "newbalanceOrig": 4000.0,
  "oldbalanceDest": 100.0,
  "newbalanceDest": 1100.0,
  "type": "PAYMENT"
}
```

**Response:**
```json
{
  "prediction": 0,
  "fraud_probability": 0.0234,
  "legitimate_probability": 0.9766,
  "is_fraud": false
}
```

#### 4. POST `/predict_batch`
Пакетное предсказание

**Request:**
```json
{
  "data": [
    {
      "amount": 1000.0,
      "oldbalanceOrig": 5000.0,
      "newbalanceOrig": 4000.0,
      "oldbalanceDest": 100.0,
      "newbalanceDest": 1100.0,
      "type": "PAYMENT"
    },
    {...}
  ]
}
```

**Response:**
```json
{
  "total": 2,
  "results": [
    {
      "index": 0,
      "prediction": 0,
      "fraud_probability": 0.0234,
      "legitimate_probability": 0.9766,
      "is_fraud": false,
      "status": "success"
    },
    {...}
  ]
}
```

## 💡 Примеры использования

### Python клиент

```python
from client_example import FraudDetectionClient

client = FraudDetectionClient('http://localhost:5000')

# Проверить здоровье
if not client.health_check():
    print("API not available")
    exit(1)

# Одиночное предсказание
transaction = {
    "amount": 9839.64,
    "oldbalanceOrig": 170136.0,
    "newbalanceOrig": 160296.36,
    "oldbalanceDest": 21524.0,
    "newbalanceDest": 0.0,
    "type": "TRANSFER"
}

result = client.predict(transaction)
print(f"Prediction: {'FRAUD' if result['is_fraud'] else 'LEGITIMATE'}")
print(f"Confidence: {result['fraud_probability']:.4f}")

# Пакетное предсказание
transactions = [transaction1, transaction2, transaction3]
batch_result = client.predict_batch(transactions)

for r in batch_result['results']:
    print(f"Result {r['index']}: {r['is_fraud']}")
```

### Bash / cURL

```bash
# Использовать example.sh скрипт для быстрого тестирования

# Или вручную:
curl -X POST http://your_api:5000/predict \
  -H "Content-Type: application/json" \
  -d @transaction.json
```

## 📊 Мониторинг

### Просмотр логов (systemd)

```bash
# Последние логи
sudo journalctl -u fraud-detection -n 50

# Постоянный мониторинг
sudo journalctl -u fraud-detection -f

# Логи за определенный период
sudo journalctl -u fraud-detection --since "1 hour ago"
```

### Docker логи

```bash
docker-compose logs fraud-detection-api
docker-compose logs -f fraud-detection-api
```

### Метрики

Посетите `http://your_api:5000/` для информации о статусе приложения.

## 🔐 Безопасность

- Используйте HTTPS в продакшене (SSL сертификат)
- Ограничьте доступ по IP в Security Group
- Регулярно обновляйте зависимости:
  ```bash
  pip install -r requirements.txt --upgrade
  ```
- Не коммитьте модель в git (добавьте в .gitignore)

## 🐛 Troubleshooting

### Модель не загружается

```bash
# Проверить, что файл существует
ls -la voting_classifier_model.pkl

# Проверить права доступа
chmod 644 voting_classifier_model.pkl

# Проверить в логах
sudo journalctl -u fraud-detection -n 100
```

### Port 5000 занят

```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Проблемы с памятью

Увеличить размер инстанса или уменьшить количество workers:

```bash
gunicorn --workers 2 --bind 0.0.0.0:5000 main:app
```

## 📈 Масштабирование

### Увеличить нагрузку

1. Увеличить количество workers:
   ```bash
   gunicorn --workers 8 --bind 0.0.0.0:5000 main:app
   ```

2. Использовать Load Balancer (AWS ALB/ELB)

3. Запустить несколько инстансов за Load Balancer

4. Использовать кеширование (Redis)

## 📝 Лицензия

MIT

## 👨‍💻 Support

Для вопросов и проблем смотрите `AWS_DEPLOYMENT.md` для подробной информации.
