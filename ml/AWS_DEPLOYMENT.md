# Руководство по развертыванию на AWS EC2

## Шаг 1: Запуск модели в test.ipynb

Сначала убедитесь, что вы запустили ячейки в `test.ipynb` до конца. Модель будет сохранена как `voting_classifier_model.pkl`.

## Шаг 2: Подготовка EC2 инстанса

### 2.1 Запустить Ubuntu EC2 инстанс
- Выбрать AMI: Ubuntu Server 22.04 LTS
- Тип инстанса: t2.medium или выше
- Открыть Security Group для портов 22 (SSH) и 5000 (приложение)

### 2.2 Подключиться к инстансу
```bash
ssh -i your_key.pem ubuntu@your_instance_ip
```

## Шаг 3: Установка зависимостей

```bash
# Обновить пакеты
sudo apt update
sudo apt upgrade -y

# Установить Python и pip
sudo apt install -y python3-pip python3-venv

# Клонировать репозиторий или загрузить файлы
# Если используете Git:
git clone your_repository

# Или загрузить файлы через SCP:
# scp -i your_key.pem -r /path/to/project ubuntu@your_instance_ip:/home/ubuntu/
```

## Шаг 4: Установка Python зависимостей

```bash
# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

## Шаг 5: Запуск приложения

### Вариант 1: Разработка (для тестирования)
```bash
python main.py
```

### Вариант 2: Продакшн (рекомендуется для AWS)
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 main:app
```

### Вариант 3: Использование systemd для автозапуска

Создать файл `/etc/systemd/system/fraud-detection.service`:

```bash
sudo nano /etc/systemd/system/fraud-detection.service
```

Добавить содержимое:

```ini
[Unit]
Description=Fraud Detection Model API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/FroudDet_AWS
Environment="PATH=/home/ubuntu/FroudDet_AWS/venv/bin"
ExecStart=/home/ubuntu/FroudDet_AWS/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Запустить сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl start fraud-detection
sudo systemctl enable fraud-detection
sudo systemctl status fraud-detection
```

## Шаг 6: Тестирование API

### Проверка здоровья приложения
```bash
curl http://your_instance_ip:5000/health
```

### Одиночное предсказание
```bash
curl -X POST http://your_instance_ip:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 9839.64,
    "oldbalanceOrig": 170136.0,
    "newbalanceOrig": 160296.36,
    "oldbalanceDest": 21524.0,
    "newbalanceDest": 0.0,
    "type": "TRANSFER"
  }'
```

### Пакетное предсказание
```bash
curl -X POST http://your_instance_ip:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "amount": 9839.64,
        "oldbalanceOrig": 170136.0,
        "newbalanceOrig": 160296.36,
        "oldbalanceDest": 21524.0,
        "newbalanceDest": 0.0,
        "type": "TRANSFER"
      },
      {
        "amount": 1000.0,
        "oldbalanceOrig": 5000.0,
        "newbalanceOrig": 4000.0,
        "oldbalanceDest": 100.0,
        "newbalanceDest": 1100.0,
        "type": "PAYMENT"
      }
    ]
  }'
```

## Шаг 7: Использование Nginx как reverse proxy (опционально)

Для лучшей производительности и безопасности:

```bash
sudo apt install -y nginx

sudo nano /etc/nginx/sites-available/fraud-detection
```

Содержимое конфига:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активировать конфиг:

```bash
sudo ln -s /etc/nginx/sites-available/fraud-detection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Шаг 8: Загрузка файлов на EC2

Используя SCP:

```bash
# Загрузить все файлы проекта
scp -i your_key.pem -r /path/to/FroudDet_AWS ubuntu@your_instance_ip:/home/ubuntu/

# Загрузить только модель
scp -i your_key.pem voting_classifier_model.pkl ubuntu@your_instance_ip:/home/ubuntu/FroudDet_AWS/
```

## API Endpoints

### GET /
Получить документацию API

### GET /health
Проверка состояния приложения

### POST /predict
Одиночное предсказание

**Параметры:**
- `amount` (float): сумма транзакции
- `oldbalanceOrig` (float): исходный баланс
- `newbalanceOrig` (float): новый баланс
- `oldbalanceDest` (float): исходный баланс получателя
- `newbalanceDest` (float): новый баланс получателя
- `type` (string): тип транзакции (CASH_IN, PAYMENT, CASH_OUT, TRANSFER, DEBIT)

**Ответ:**
```json
{
  "prediction": 0 or 1,
  "fraud_probability": float,
  "legitimate_probability": float,
  "is_fraud": boolean
}
```

### POST /predict_batch
Пакетное предсказание для нескольких транзакций

## Мониторинг и логирование

Просмотр логов syslog:
```bash
sudo journalctl -u fraud-detection -f
```

Просмотр логов Nginx:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Безопасность

- Использовать HTTPS (установить SSL сертификат через Let's Encrypt)
- Ограничить доступ по IP в Security Group
- Регулярно обновлять зависимости
- Использовать environment переменные для конфигурации

## Масштабирование

Для высокой нагрузки:
- Увеличить количество workers в gunicorn: `--workers 8+`
- Использовать load balancer (ELB/ALB)
- Запустить несколько инстансов за load balancer
- Использовать кеширование (Redis)
