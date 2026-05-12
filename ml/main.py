from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import logging
import traceback

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the model
model = None


def load_model():
    """Load the trained model"""
    global model
    try:
        model = joblib.load('voting_classifier_model.pkl')
        logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False


def preprocess_input(data):
    """
    Preprocess input data for prediction
    Expected input features: amount, oldbalanceOrig, newbalanceOrig, 
                           oldbalanceDest, newbalanceDest, type
    """
    try:
        # Create a DataFrame from input
        df = pd.DataFrame([data])
        
        # Convert numeric fields
        numeric_fields = ['amount', 'oldbalanceOrig', 'newbalanceOrig', 
                         'oldbalanceDest', 'newbalanceDest']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # One-hot encode transaction type
        transaction_type = str(df['type'].values[0]).upper()
        
        # Create binary columns for transaction types
        df['is_CASH_IN'] = 1 if transaction_type == 'CASH_IN' else 0
        df['is_PAYMENT'] = 1 if transaction_type == 'PAYMENT' else 0
        df['is_CASH_OUT'] = 1 if transaction_type == 'CASH_OUT' else 0
        df['is_TRANSFER'] = 1 if transaction_type == 'TRANSFER' else 0
        df['is_DEBIT'] = 1 if transaction_type == 'DEBIT' else 0
        
        # Drop the original type column
        df = df.drop(columns=['type'])
        
        # Ensure all required columns are present
        required_columns = ['amount', 'oldbalanceOrig', 'newbalanceOrig', 
                           'oldbalanceDest', 'newbalanceDest', 
                           'is_CASH_IN', 'is_PAYMENT', 'is_CASH_OUT', 
                           'is_TRANSFER', 'is_DEBIT']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Select only required columns in the correct order
        df = df[required_columns]
        
        # Handle NaN values
        if df.isnull().any().any():
            raise ValueError("Input contains NaN values")
        
        return df
    
    except Exception as e:
        logger.error(f"Error preprocessing input: {str(e)}")
        raise


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    if model is None:
        return jsonify({'status': 'unhealthy', 'message': 'Model not loaded'}), 503
    return jsonify({'status': 'healthy', 'message': 'Model loaded and ready'}), 200


@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint
    Expected JSON format:
    {
        "amount": float,
        "oldbalanceOrig": float,
        "newbalanceOrig": float,
        "oldbalanceDest": float,
        "newbalanceDest": float,
        "type": string (CASH_IN, PAYMENT, CASH_OUT, TRANSFER, DEBIT)
    }
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['amount', 'oldbalanceOrig', 'newbalanceOrig', 
                          'oldbalanceDest', 'newbalanceDest', 'type']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({'error': f'Missing fields: {missing_fields}'}), 400
        
        # Preprocess input
        X = preprocess_input(data)
        
        # Make prediction
        prediction = model.predict(X)[0]
        probability = model.predict_proba(X)[0]
        
        response = {
            'prediction': int(prediction),
            'fraud_probability': float(probability[1]),
            'legitimate_probability': float(probability[0]),
            'is_fraud': bool(prediction == 1)
        }
        
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Prediction error: {traceback.format_exc()}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint
    Expected JSON format:
    {
        "data": [
            {
                "amount": float,
                "oldbalanceOrig": float,
                "newbalanceOrig": float,
                "oldbalanceDest": float,
                "newbalanceDest": float,
                "type": string
            },
            ...
        ]
    }
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.get_json()
        
        if data is None or 'data' not in data:
            return jsonify({'error': 'No data provided or missing "data" field'}), 400
        
        batch_data = data['data']
        
        if not isinstance(batch_data, list):
            return jsonify({'error': '"data" must be a list'}), 400
        
        results = []
        
        for idx, item in enumerate(batch_data):
            try:
                X = preprocess_input(item)
                prediction = model.predict(X)[0]
                probability = model.predict_proba(X)[0]
                
                results.append({
                    'index': idx,
                    'prediction': int(prediction),
                    'fraud_probability': float(probability[1]),
                    'legitimate_probability': float(probability[0]),
                    'is_fraud': bool(prediction == 1),
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'index': idx,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'total': len(batch_data),
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f"Batch prediction error: {traceback.format_exc()}")
        return jsonify({'error': f'Batch prediction failed: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        'app': 'Fraud Detection Model API',
        'version': '1.0',
        'endpoints': {
            'GET /': 'This documentation',
            'GET /health': 'Health check',
            'POST /predict': 'Single prediction',
            'POST /predict_batch': 'Batch predictions'
        },
        'example_request': {
            'amount': 9839.64,
            'oldbalanceOrig': 170136.0,
            'newbalanceOrig': 160296.36,
            'oldbalanceDest': 21524.0,
            'newbalanceDest': 0.0,
            'type': 'TRANSFER'
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Load model on startup
    if not load_model():
        logger.warning("Failed to load model, starting server anyway")
    
    # Start Flask app
    # For production on AWS EC2, use a production WSGI server like Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=False)
