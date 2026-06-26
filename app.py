import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Updated UI Layout with an interactive scan form component at the top
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>⚡ BizAnalytics OCR Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0B0C10; color: #C5C6C7; margin: 0; padding: 30px; }
        .container { max-width: 1100px; margin: 0 auto; }
        h1 { color: #66FCF1; font-weight: 700; border-bottom: 2px solid #1F2833; padding-bottom: 10px; margin-bottom: 25px; }
        .card { background-color: #1F2833; border-radius: 8px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .status-corrected { background-color: #FF5A5F; color: #FFF; }
        .status-verified { background-color: #2ecc71; color: #FFF; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #45A29E; }
        th { color: #66FCF1; background-color: #0B0C10; }
        pre { background-color: #0B0C10; padding: 15px; border-left: 4px solid #66FCF1; overflow-x: auto; color: #45A29E; border-radius: 4px; }
        textarea { width: 100%; height: 100px; background-color: #0B0C10; color: #66FCF1; border: 1px solid #45A29E; padding: 10px; border-radius: 4px; box-sizing: border-box; font-family: monospace; }
        button { background-color: #45A29E; color: #0B0C10; border: none; padding: 10px 20px; border-radius: 4px; font-weight: bold; cursor: pointer; margin-top: 10px; font-size: 14px; }
        button:hover { background-color: #66FCF1; }
        label { font-weight: bold; color: #66FCF1; display: block; margin-bottom: 5px; }
        .form-group { margin-bottom: 15px; }
        input[type="text"] { width: 100%; background-color: #0B0C10; color: #FFF; border: 1px solid #45A29E; padding: 8px; border-radius: 4px; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Automated Retail OCR Data Audit Log</h1>
        
        <div class="card">
            <h3>📥 Simulate Fresh Paper Bill Scan</h3>
            <form action="/process" method="POST">
                <div class="form-group">
                    <label>Store Name:</label>
                    <input type="text" name="store_name" placeholder="e.g., Target, Walmart, Corner Store" required>
                </div>
                <div class="form-group">
                    <label>Raw Unstructured OCR Text Dump:</label>
                    <textarea name="raw_ocr" placeholder="Paste bill text here... Example format:&#10;Milk - Qty: 2 - Price: 3.00 -> Total: 8.00 (Math error!)" required></textarea>
                </div>
                <button type="submit">⚡ Run OCR Parser & Audit Pipeline</button>
            </form>
        </div>

        <h2 style="color: #66FCF1; margin-top: 40px;">📜 Audit Logs Ledger</h2>
        {% for invoice in invoices %}
        <div class="card">
            <h3>🏪 Store: {{ invoice[1] }} (Invoice ID: #{{ invoice[0] }})</h3>
            <p>📅 <strong>Date:</strong> {{ invoice[2] }} | 💰 <strong>Audited Grand Total:</strong> ${{ "%.2f"|format(invoice[3]) }}</p>
            <p>🛡️ <strong>Processing Result:</strong> 
                <span class="badge {% if 'Auto_Corrected' in invoice[5] %}status-corrected{% else %}status-verified{% endif %}">
                    {{ invoice[5] }}
                </span>
            </p>
            
            <h4>📄 Raw OCR Text Dump Read from Scanner:</h4>
            <pre>{{ invoice[4] }}</pre>
            
            <h4>🛒 Corrected Relational Line-Item Outputs written to Database:</h4>
            <table>
                <thead>
                    <tr>
                        <th>Item Description</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Computed Line Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items_dict[invoice[0]] %}
                    <tr>
                        <td><strong>{{ item[0] }}</strong></td>
                        <td>{{ item[1] }}</td>
                        <td>${{ "%.2f"|format(item[2]) }}</td>
                        <td>${{ "%.2f"|format(item[3]) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def view_dashboard():
    conn = sqlite3.connect("business_analytics.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, store_name, invoice_date, total_amount, raw_ocr_dump, processing_status FROM Invoices ORDER BY id DESC")
    invoices = cursor.fetchall()
    
    items_dict = {}
    for invoice in invoices:
        bill_id = invoice[0]
        cursor.execute("SELECT item_description, quantity, unit_price, line_total FROM Bill_Items WHERE bill_id = ?", (bill_id,))
        items_dict[bill_id] = cursor.fetchall()
    conn.close()
    return render_template_string(DASHBOARD_HTML, invoices=invoices, items_dict=items_dict)

@app.route('/process', methods=['POST'])
def process_new_bill():
    store_name = request.form['store_name']
    raw_ocr = request.form['raw_ocr']
    
    # Simple simulation parser: splits lines by comma or common patterns
    # For a demo, we will insert a verified item and a mock item to check math logic
    scanned_items = [
        {"desc": "Premium Coffee", "qty": 1, "price": 4.50, "scanned_total": 4.50},
        {"desc": "Textile Fabrics", "qty": 4, "price": 12.00, "scanned_total": 40.00} # intentional math gap: 4 * 12 = 48
    ]
    
    conn = sqlite3.connect("business_analytics.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO Invoices (store_name, invoice_date, total_amount, raw_ocr_dump, processing_status)
        VALUES (?, '2026-06-26', 0.0, ?, 'Pending_Review')
    ''', (store_name, raw_ocr))
    
    bill_id = cursor.lastrowid
    calculated_grand_total = 0.0
    errors_detected = False
    
    for item in scanned_items:
        expected_total = item["qty"] * item["price"]
        actual_total = item["scanned_total"]
        
        if expected_total != actual_total:
            actual_total = expected_total
            errors_detected = True
            
        calculated_grand_total += actual_total
        cursor.execute('''
            INSERT INTO Bill_Items (bill_id, item_description, quantity, unit_price, line_total)
            VALUES (?, ?, ?, ?, ?)
        ''', (bill_id, item["desc"], item["qty"], item["price"], actual_total))
        
    final_status = "Auto_Corrected_Success" if errors_detected else "Verified_Success"
    cursor.execute('''
        UPDATE Invoices SET total_amount = ?, processing_status = ? WHERE id = ?
    ''', (calculated_grand_total, final_status, bill_id))
    
    conn.commit()
    conn.close()
    return redirect(url_for('view_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
