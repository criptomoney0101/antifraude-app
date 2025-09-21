from flask import Flask, jsonify, request
import time
import random

app = Flask(__name__)

# Simular una base de datos de transacciones
transactions_db = []
fraud_patterns = [
    {"pattern": "multiple_transactions_same_ip", "risk": "high"},
    {"pattern": "unusual_amount", "risk": "medium"},
    {"pattern": "new_account_large_transfer", "risk": "high"}
]

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/transaction', methods=['POST'])
def process_transaction():
    data = request.json
    
    # Simular procesamiento de transacción
    transaction = {
        "id": len(transactions_db) + 1,
        "amount": data.get("amount", 0),
        "from_account": data.get("from_account", ""),
        "to_account": data.get("to_account", ""),
        "timestamp": time.time(),
        "ip": data.get("ip", "")
    }
    
    # Simular detección de fraude
    fraud_detected = False
    fraud_reason = None
    
    # Patrón 1: Múltiples transacciones desde la misma IP
    recent_transactions = [t for t in transactions_db if t["ip"] == transaction["ip"] and time.time() - t["timestamp"] < 3600]
    if len(recent_transactions) > 5:
        fraud_detected = True
        fraud_reason = "multiple_transactions_same_ip"
    
    # Patrón 2: Monto inusual
    if transaction["amount"] > 10000:
        fraud_detected = True
        fraud_reason = "unusual_amount"
    
    # Patrón 3: Cuenta nueva con transferencia grande
    if transaction["from_account"].startswith("new_") and transaction["amount"] > 5000:
        fraud_detected = True
        fraud_reason = "new_account_large_transfer"
    
    transaction["fraud_detected"] = fraud_detected
    transaction["fraud_reason"] = fraud_reason
    
    transactions_db.append(transaction)
    
    return jsonify({
        "transaction_id": transaction["id"],
        "fraud_detected": fraud_detected,
        "fraud_reason": fraud_reason,
        "status": "processed"
    })

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    return jsonify({"transactions": transactions_db})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_transactions = len(transactions_db)
    fraud_transactions = len([t for t in transactions_db if t["fraud_detected"]])
    
    return jsonify({
        "total_transactions": total_transactions,
        "fraud_transactions": fraud_transactions,
        "fraud_rate": (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
