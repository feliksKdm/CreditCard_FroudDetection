"""
Example client for Fraud Detection API

This script demonstrates how to make requests to the deployed model API.
"""

import requests
import json
from typing import Dict, List, Any


class FraudDetectionClient:
    """Client for interacting with the Fraud Detection API"""
    
    def __init__(self, base_url: str):
        """
        Initialize the client
        
        Args:
            base_url: The base URL of the API (e.g., 'http://localhost:5000')
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """
        Check if the API is running and healthy
        
        Returns:
            True if the API is healthy, False otherwise
        """
        try:
            response = self.session.get(f'{self.base_url}/health', timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def predict(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a single prediction
        
        Args:
            transaction_data: Dictionary with keys:
                - amount: float
                - oldbalanceOrig: float
                - newbalanceOrig: float
                - oldbalanceDest: float
                - newbalanceDest: float
                - type: str (CASH_IN, PAYMENT, CASH_OUT, TRANSFER, DEBIT)
        
        Returns:
            Dictionary with prediction results
        """
        try:
            response = self.session.post(
                f'{self.base_url}/predict',
                json=transaction_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Prediction error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def predict_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Make batch predictions
        
        Args:
            transactions: List of transaction dictionaries
        
        Returns:
            Dictionary with batch prediction results
        """
        try:
            response = self.session.post(
                f'{self.base_url}/predict_batch',
                json={'data': transactions},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Batch prediction error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def print_prediction(self, prediction: Dict[str, Any]) -> None:
        """Print a prediction result in a readable format"""
        if prediction is None:
            print("No prediction result")
            return
        
        if 'error' in prediction:
            print(f"Error: {prediction['error']}")
            return
        
        print(f"Prediction: {'FRAUD' if prediction.get('is_fraud') else 'LEGITIMATE'}")
        print(f"Fraud Probability: {prediction.get('fraud_probability', 0):.4f}")
        print(f"Legitimate Probability: {prediction.get('legitimate_probability', 0):.4f}")
        print()


def main():
    """Example usage"""
    
    # Change this to your API URL
    API_URL = 'http://localhost:5000'
    # For AWS EC2: API_URL = 'http://your_instance_ip:5000'
    
    client = FraudDetectionClient(API_URL)
    
    # Check if API is running
    print("Checking API health...")
    if not client.health_check():
        print("API is not healthy or not running")
        return
    print("✓ API is running and healthy\n")
    
    # Example transaction (legitimate)
    print("=" * 60)
    print("EXAMPLE 1: Legitimate Transaction")
    print("=" * 60)
    
    transaction1 = {
        "amount": 1000.0,
        "oldbalanceOrig": 5000.0,
        "newbalanceOrig": 4000.0,
        "oldbalanceDest": 100.0,
        "newbalanceDest": 1100.0,
        "type": "PAYMENT"
    }
    
    print(f"Transaction: {json.dumps(transaction1, indent=2)}")
    print("\nPrediction:")
    
    result = client.predict(transaction1)
    client.print_prediction(result)
    
    # Example transaction (potentially fraudulent)
    print("=" * 60)
    print("EXAMPLE 2: Large Transfer")
    print("=" * 60)
    
    transaction2 = {
        "amount": 900000.0,
        "oldbalanceOrig": 1000000.0,
        "newbalanceOrig": 100000.0,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 900000.0,
        "type": "TRANSFER"
    }
    
    print(f"Transaction: {json.dumps(transaction2, indent=2)}")
    print("\nPrediction:")
    
    result = client.predict(transaction2)
    client.print_prediction(result)
    
    # Batch prediction example
    print("=" * 60)
    print("EXAMPLE 3: Batch Prediction (Multiple Transactions)")
    print("=" * 60)
    
    batch_transactions = [
        {
            "amount": 500.0,
            "oldbalanceOrig": 2000.0,
            "newbalanceOrig": 1500.0,
            "oldbalanceDest": 500.0,
            "newbalanceDest": 1000.0,
            "type": "TRANSFER"
        },
        {
            "amount": 100000.0,
            "oldbalanceOrig": 150000.0,
            "newbalanceOrig": 50000.0,
            "oldbalanceDest": 1000.0,
            "newbalanceDest": 101000.0,
            "type": "CASH_IN"
        },
        {
            "amount": 5000.0,
            "oldbalanceOrig": 10000.0,
            "newbalanceOrig": 5000.0,
            "oldbalanceDest": 0.0,
            "newbalanceDest": 0.0,
            "type": "CASH_OUT"
        }
    ]
    
    print(f"Number of transactions: {len(batch_transactions)}")
    print("\nProcessing batch...")
    
    batch_result = client.predict_batch(batch_transactions)
    
    if batch_result:
        print(f"\nTotal processed: {batch_result.get('total', 0)}")
        print(f"Results: {len(batch_result.get('results', []))}\n")
        
        for i, result in enumerate(batch_result.get('results', [])):
            print(f"Transaction {i+1}:")
            if result.get('status') == 'success':
                print(f"  Prediction: {'FRAUD' if result.get('is_fraud') else 'LEGITIMATE'}")
                print(f"  Fraud Probability: {result.get('fraud_probability', 0):.4f}")
            else:
                print(f"  Error: {result.get('error')}")
            print()


if __name__ == '__main__':
    main()
