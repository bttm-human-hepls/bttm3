from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')

@app.route('/api/send-telegram', methods=['POST', 'OPTIONS'])
def send_telegram():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        transaction_data = data.get('transactionData')
        tx_id = data.get('txId')
        user_email = data.get('userEmail', 'N/A')
        
        amount = transaction_data.get('amount', 0)
        charge = max(5, (amount // 1000) * 5) if amount >= 50 else 0
        date = datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')
        
        message = f"""╔══════════════════════════════════╗
║     ⚡ B.T.T.M NEW TRANSACTION ⚡     ║
╚══════════════════════════════════════╝

🆔 ID: {tx_id}
📅 Date: {date}
👤 Sender: {transaction_data.get('fullName', 'N/A')}
📱 Sender No: {transaction_data.get('senderNumber', 'N/A')}
💰 Amount: ৳{amount}
"""
        
        if charge > 0:
            message += f"""💸 Service Charge: ৳{charge}
📊 Net Amount: ৳{amount - charge}
"""
        
        message += f"""
📱 Receiver: {transaction_data.get('receiverNumber', 'N/A')}
🔖 TrxID: {transaction_data.get('trxId', 'N/A')}
📧 User: {user_email}
📊 Status: ⏳ PENDING

────────────────────────────────────
✅ Approve | ❌ Reject | 📋 Details
────────────────────────────────────"""
        
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Telegram API error"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "B.T.T.M Backend"
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "B.T.T.M Backend is running!",
        "endpoints": {
            "send_telegram": "POST /api/send-telegram",
            "health": "GET /health"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))