# Fraud Detection Model API

Flask application for deploying a fraud detection model on AWS EC2.

## 📋 Table of Contents

- [Requirements](#requirements)
- [Local Testing](#local-testing)
- [Deployment on AWS EC2](#deployment-on-aws-ec2)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Monitoring](#monitoring)

## 🔧 Requirements

### For local launch:
- Python 3.8+
- pip
- 4GB+ RAM

### For AWS EC2:
- Ubuntu Server 20.04 LTS or higher
- t2.medium instance or larger
- 20GB+ disk space

## 🚀 Local Testing

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Model Preparation

Make sure the `voting_classifier_model.pkl` file is in the project root folder.

If the model is not yet created, run the cells in `test.ipynb`:

```bash
jupyter notebook test.ipynb
```

### 3. Run Application

```bash
# Development (with debug mode)
python main.py

# Production (recommended)
gunicorn --workers 4 --bind 127.0.0.1:5000 main:app
```

### 4. Test API

```bash
# Health check
curl http://localhost:5000/health

# Single prediction
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

## 🌐 Deployment on AWS EC2

### Option 1: Automated Deployment

```bash
# 1. Upload script to EC2
scp -i your_key.pem deploy.sh ubuntu@your_instance_ip:~/

# 2. Connect to EC2
ssh -i your_key.pem ubuntu@your_instance_ip

# 3. Run script
chmod +x deploy.sh
./deploy.sh

# 4. Upload project files
# On local machine:
scp -i your_key.pem main.py requirements.txt ubuntu@your_instance_ip:~/FroudDet_AWS/
scp -i your_key.pem voting_classifier_model.pkl ubuntu@your_instance_ip:~/FroudDet_AWS/

# 5. Start service
ssh -i your_key.pem ubuntu@your_instance_ip
sudo systemctl start fraud-detection
sudo systemctl enable fraud-detection
```

### Option 2: Docker Deployment

```bash
# 1. On local machine, prepare files and upload
scp -i your_key.pem Dockerfile docker-compose.yml requirements.txt main.py voting_classifier_model.pkl ubuntu@your_instance_ip:~/FroudDet_AWS/

# 2. On EC2 instance, install Docker
ssh -i your_key.pem ubuntu@your_instance_ip
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 3. Start container
cd ~/FroudDet_AWS
docker-compose up -d

# 4. Check status
docker-compose logs -f
```

### Option 3: Manual Deployment

See full documentation in the `AWS_DEPLOYMENT.md` file

## 📚 API Documentation

### Endpoints

#### 1. GET `/`
Get API information and documentation

**Response:**
```json
{
  "app": "Fraud Detection Model API",
  "version": "1.0",
  "endpoints": {...}
}
```

#### 2. GET `/health`
Application health check

**Response:**
```json
{
  "status": "healthy",
  "message": "Model loaded and ready"
}
```

#### 3. POST `/predict`
Single prediction

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
Batch prediction

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

## 💡 Usage Examples

### Python Client

```python
from client_example import FraudDetectionClient

client = FraudDetectionClient('http://localhost:5000')

# Check health
if not client.health_check():
    print("API not available")
    exit(1)

# Single prediction
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

# Batch prediction
transactions = [transaction1, transaction2, transaction3]
batch_result = client.predict_batch(transactions)

for r in batch_result['results']:
    print(f"Result {r['index']}: {r['is_fraud']}")
```

### Bash / cURL

```bash
# Use example.sh script for quick testing

# Or manually:
curl -X POST http://your_api:5000/predict \
  -H "Content-Type: application/json" \
  -d @transaction.json
```

## 📊 Monitoring

### View Logs (systemd)

```bash
# Latest logs
sudo journalctl -u fraud-detection -n 50

# Continuous monitoring
sudo journalctl -u fraud-detection -f

# Logs for specific period
sudo journalctl -u fraud-detection --since "1 hour ago"
```

### Docker Logs

```bash
docker-compose logs fraud-detection-api
docker-compose logs -f fraud-detection-api
```

### Metrics

Visit `http://your_api:5000/` for application status information.

## 🔐 Security

- Use HTTPS in production (SSL certificate)
- Restrict access by IP in Security Group
- Regularly update dependencies:
  ```bash
  pip install -r requirements.txt --upgrade
  ```
- Do not commit model to git (add to .gitignore)

## 🐛 Troubleshooting

### Model not loading

```bash
# Check that file exists
ls -la voting_classifier_model.pkl

# Check permissions
chmod 644 voting_classifier_model.pkl

# Check in logs
sudo journalctl -u fraud-detection -n 100
```

### Port 5000 occupied

```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Memory issues

Increase instance size or reduce number of workers:

```bash
gunicorn --workers 2 --bind 0.0.0.0:5000 main:app
```

## 📈 Scaling

### Increase load

1. Increase number of workers:
   ```bash
   gunicorn --workers 8 --bind 0.0.0.0:5000 main:app
   ```

2. Use Load Balancer (AWS ALB/ELB)

3. Run multiple instances behind Load Balancer

4. Use caching (Redis)

## 📝 License

MIT

## 👨‍💻 Support

For questions and issues, see `AWS_DEPLOYMENT.md` for detailed information.

## 📋 Table of Contents

- [Requirements](#requirements)
- [Local Testing](#local-testing)
- [Deployment on AWS EC2](#deployment-on-aws-ec2)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Monitoring](#monitoring)

## 🔧 Requirements

### For local launch:
- Python 3.8+
- pip
- 4GB+ RAM

### For AWS EC2:
- Ubuntu Server 20.04 LTS or higher
- t2.medium instance or larger
- 20GB+ disk space

## 🚀 Local Testing

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Model Preparation

Make sure the `voting_classifier_model.pkl` file is in the project root folder.

If the model is not yet created, run the cells in `test.ipynb`:

```bash
jupyter notebook test.ipynb
```

### 3. Run Application

```bash
# Development (with debug mode)
python main.py

# Production (recommended)
gunicorn --workers 4 --bind 127.0.0.1:5000 main:app
```

### 4. Test API

```bash
# Health check
curl http://localhost:5000/health

# Single prediction
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

## 🌐 Deployment on AWS EC2

### Option 1: Automated Deployment

```bash
# 1. Upload script to EC2
scp -i your_key.pem deploy.sh ubuntu@your_instance_ip:~/

# 2. Connect to EC2
ssh -i your_key.pem ubuntu@your_instance_ip

# 3. Run script
chmod +x deploy.sh
./deploy.sh

# 4. Upload project files
# On local machine:
scp -i your_key.pem main.py requirements.txt ubuntu@your_instance_ip:~/FroudDet_AWS/
scp -i your_key.pem voting_classifier_model.pkl ubuntu@your_instance_ip:~/FroudDet_AWS/

# 5. Start service
ssh -i your_key.pem ubuntu@your_instance_ip
sudo systemctl start fraud-detection
sudo systemctl enable fraud-detection
```

### Option 2: Docker Deployment

```bash
# 1. On local machine, prepare files and upload
scp -i your_key.pem Dockerfile docker-compose.yml requirements.txt main.py voting_classifier_model.pkl ubuntu@your_instance_ip:~/FroudDet_AWS/

# 2. On EC2 instance, install Docker
ssh -i your_key.pem ubuntu@your_instance_ip
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 3. Start container
cd ~/FroudDet_AWS
docker-compose up -d

# 4. Check status
docker-compose logs -f
```

### Option 3: Manual Deployment

See full documentation in the `AWS_DEPLOYMENT.md` file

## 📚 API Documentation

### Endpoints

#### 1. GET `/`
Get API information and documentation

**Response:**
```json
{
  "app": "Fraud Detection Model API",
  "version": "1.0",
  "endpoints": {...}
}
```

#### 2. GET `/health`
Application health check

**Response:**
```json
{
  "status": "healthy",
  "message": "Model loaded and ready"
}
```

#### 3. POST `/predict`
Single prediction

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
Batch prediction

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

## 💡 Usage Examples

### Python Client

```python
from client_example import FraudDetectionClient

client = FraudDetectionClient('http://localhost:5000')

# Check health
if not client.health_check():
    print("API not available")
    exit(1)

# Single prediction
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

# Batch prediction
transactions = [transaction1, transaction2, transaction3]
batch_result = client.predict_batch(transactions)

for r in batch_result['results']:
    print(f"Result {r['index']}: {r['is_fraud']}")
```

### Bash / cURL

```bash
# Use example.sh script for quick testing

# Or manually:
curl -X POST http://your_api:5000/predict \
  -H "Content-Type: application/json" \
  -d @transaction.json
```

## 📊 Monitoring

### View Logs (systemd)

```bash
# Latest logs
sudo journalctl -u fraud-detection -n 50

# Continuous monitoring
sudo journalctl -u fraud-detection -f

# Logs for specific period
sudo journalctl -u fraud-detection --since "1 hour ago"
```

### Docker Logs

```bash
docker-compose logs fraud-detection-api
docker-compose logs -f fraud-detection-api
```

### Metrics

Visit `http://your_api:5000/` for application status information.

## 🔐 Security

- Use HTTPS in production (SSL certificate)
- Restrict access by IP in Security Group
- Regularly update dependencies:
  ```bash
  pip install -r requirements.txt --upgrade
  ```
- Do not commit model to git (add to .gitignore)

## 🐛 Troubleshooting

### Model not loading

```bash
# Check that file exists
ls -la voting_classifier_model.pkl

# Check permissions
chmod 644 voting_classifier_model.pkl

# Check in logs
sudo journalctl -u fraud-detection -n 100
```

### Port 5000 occupied

```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Memory issues

Increase instance size or reduce number of workers:

```bash
gunicorn --workers 2 --bind 0.0.0.0:5000 main:app
```

## 📈 Scaling

### Increase load

1. Increase number of workers:
   ```bash
   gunicorn --workers 8 --bind 0.0.0.0:5000 main:app
   ```

2. Use Load Balancer (AWS ALB/ELB)

3. Run multiple instances behind Load Balancer

4. Use caching (Redis)

## 📝 License

MIT

## 👨‍💻 Support

For questions and issues, see `AWS_DEPLOYMENT.md` for detailed information.
