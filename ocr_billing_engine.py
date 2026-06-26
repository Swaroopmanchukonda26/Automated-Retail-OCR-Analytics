import sqlite3

def build_database_tables_if_missing(cursor):
    """Ensures the relational tables exist before writing to them."""
    # 1. Create Parent Table: Invoices
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT NOT NULL,
            invoice_date TEXT,
            total_amount REAL,
            raw_ocr_dump TEXT,
            processing_status TEXT DEFAULT 'Pending_Verification'
        )
    ''')

    # 2. Create Child Table: Individual Bill Items (One-to-Many Relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bill_Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            item_description TEXT NOT NULL,
            quantity INTEGER,
            unit_price REAL,
            line_total REAL,
            FOREIGN KEY (bill_id) REFERENCES Invoices(id) ON DELETE CASCADE
        )
    ''')

def run_ocr_validation_pipeline():
    print("🔄 Simulating OCR Input Extraction and Data Correction Pipeline...\n")
    
    mock_raw_ocr_text = """
    === SUPER MART GROCERY STORE ===
    DATE: 2026-06-25
    ITEMS SHOPPED:
    1. Organic Milk  - Qty: 2 - Price: 3.50 -> Total: 7.00
    2. Whole Grain Bread - Qty: 3 - Price: 2.50 -> Total: 9.00  [OCR ERROR: 3 * 2.50 = 7.50]
    3. Fresh Apples  - Qty: 5 - Price: 1.20 -> Total: 6.00
    ================================
    """
    
    store_name = "Super Mart Grocery Store"
    invoice_date = "2026-06-25"
    
    scanned_items = [
        {"desc": "Organic Milk", "qty": 2, "price": 3.50, "scanned_total": 7.00},
        {"desc": "Whole Grain Bread", "qty": 3, "price": 2.50, "scanned_total": 9.00},
        {"desc": "Fresh Apples", "qty": 5, "price": 1.20, "scanned_total": 6.00}
    ]
    
    # Connect to database file
    conn = sqlite3.connect("business_analytics.db")
    cursor = conn.cursor()
    
    # AUTOMATED FIX: Safely construct tables if they do not exist in storage
    build_database_tables_if_missing(cursor)
    
    # Insert Parent Invoice entry record header
    cursor.execute('''
        INSERT INTO Invoices (store_name, invoice_date, total_amount, raw_ocr_dump, processing_status)
        VALUES (?, ?, ?, ?, ?)
    ''', (store_name, invoice_date, 0.0, mock_raw_ocr_text, "Pending_Review"))
    
    bill_id = cursor.lastrowid
    calculated_grand_total = 0.0
    errors_detected = False
    
    print("📋 Evaluating Line-Item Computations:")
    print("-" * 65)
    
    for item in scanned_items:
        expected_total = item["qty"] * item["price"]
        actual_total = item["scanned_total"]
        
        if expected_total != actual_total:
            print(f"⚠️  DISCREPANCY FOUND on '{item['desc']}': Scanned Total ({actual_total:.2f}) != Calculated Total ({expected_total:.2f})")
            print(f"   ⚙️  Automated Action: Auto-corrected line total value to {expected_total:.2f}")
            actual_total = expected_total
            errors_detected = True
        else:
            print(f"✅ Line Item Verified: '{item['desc']}' -> Total matches perfectly ({actual_total:.2f})")
            
        calculated_grand_total += actual_total
        
        cursor.execute('''
            INSERT INTO Bill_Items (bill_id, item_description, quantity, unit_price, line_total)
            VALUES (?, ?, ?, ?, ?)
        ''', (bill_id, item["desc"], item["qty"], item["price"], actual_total))
        
    final_status = "Auto_Corrected_Success" if errors_detected else "Verified_Success"
    cursor.execute('''
        UPDATE Invoices 
        SET total_amount = ?, processing_status = ? 
        WHERE id = ?
    ''', (calculated_grand_total, final_status, bill_id))
    
    conn.commit()
    conn.close()
    
    print("-" * 65)
    print(f"🎉 Relational Sync Complete! Grand Total: ${calculated_grand_total:.2f} | Status Flag: {final_status}")

if __name__ == "__main__":
    run_ocr_validation_pipeline()