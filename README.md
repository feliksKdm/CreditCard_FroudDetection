# Fraud Detection AWS Project

A comprehensive machine learning project for fraud detection deployed on AWS EC2 using Flask API.

## 📁 Project Structure

```
FroudDet_AWS/
├── ml/                          # Machine Learning API Service
│   ├── main.py                  # Flask application entry point
│   ├── client_example.py        # Python client for API testing
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Docker container configuration
│   ├── docker-compose.yml       # Docker Compose setup
│   ├── deploy.sh               # AWS deployment script
│   ├── test_api.sh             # API testing script
│   ├── test.ipynb              # Jupyter notebook for model training/testing
│   ├── QUICK_START.md          # Quick start guide
│   ├── AWS_DEPLOYMENT.md       # Detailed AWS deployment guide
│   ├── README.md               # API documentation
│   ├── catboost_info/          # Model training artifacts
│   │   ├── catboost_training.json
│   │   ├── learn_error.tsv
│   │   ├── time_left.tsv
│   │   ├── learn/
│   │   └── tmp/
│   └── dataset/                # Dataset storage
│       └── financial-fraud-detection-dataset/
│           ├── 1.complete
│           └── versions/
│               └── 1/
│                   └── Synthetic_Financial_datasets_log.csv
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker (optional)
- AWS CLI (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FroudDet_AWS
   ```

2. **Set up the ML API**
   ```bash
   cd ml
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Train or load the model**
   ```bash
   jupyter notebook test.ipynb
   # Run all cells to train the model or load existing one
   ```

4. **Start the API server**
   ```bash
   python main.py
   ```

5. **Test the API**
   ```bash
   curl http://localhost:5000/health
   ```

### Docker Deployment

```bash
cd ml
docker-compose up -d
```

### AWS EC2 Deployment

See [ml/AWS_DEPLOYMENT.md](ml/AWS_DEPLOYMENT.md) for detailed AWS deployment instructions.

## 📊 Dataset

The project uses the Synthetic Financial Datasets for Fraud Detection, containing simulated financial transactions with fraud labels.

- **Location**: `ml/dataset/financial-fraud-detection-dataset/`
- **Format**: CSV with transaction features
- **Features**: amount, balances, transaction type, etc.

## 🧠 Machine Learning Model

- **Algorithm**: Voting Classifier (ensemble of multiple models)
- **Framework**: CatBoost, scikit-learn
- **Input**: Transaction features (amount, balances, type)
- **Output**: Fraud probability and binary classification

## 🔧 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /predict` - Single prediction
- `POST /predict_batch` - Batch predictions

See [ml/README.md](ml/README.md) for complete API documentation.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │────│   Flask API     │────│   ML Model      │
│                 │    │   (EC2/AWS)     │    │   (CatBoost)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Monitoring    │
                       │   (Logs/Metrics)│
                       └─────────────────┘
```

## 📈 Features

- **Real-time Fraud Detection**: REST API for instant predictions
- **Batch Processing**: Handle multiple transactions simultaneously
- **Scalable Deployment**: Docker and AWS EC2 support
- **Model Training**: Jupyter notebook for model development
- **Monitoring**: Comprehensive logging and health checks
- **Security**: HTTPS support and access controls

## 🛠️ Technologies Used

- **Backend**: Flask, Gunicorn
- **ML**: CatBoost, scikit-learn, pandas, numpy
- **Deployment**: Docker, AWS EC2, systemd
- **Development**: Jupyter Notebook
- **Data**: Synthetic financial datasets

## 📝 Documentation

- [API Documentation](ml/README.md)
- [AWS Deployment Guide](ml/AWS_DEPLOYMENT.md)
- [Quick Start Guide](ml/QUICK_START.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see [ml/README.md](ml/README.md) for details.

## 👥 Support

For questions and issues:
1. Check the documentation in the `ml/` folder
2. Review existing issues
3. Create a new issue with detailed information