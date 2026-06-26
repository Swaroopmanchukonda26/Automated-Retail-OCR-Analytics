# ⚡ Automated Retail OCR Data Audit Log & Relational Pipeline

A full-stack Python data engineering application designed to automatically parse, validate, and programmatically correct mathematical discrepancies from unstructured paper billing OCR text dumps.

## 🗄️ Relational Database Architecture
The application uses a local SQLite relational layer with an enforced One-to-Many entity constraint:
* **`Invoices` (Parent):** Manages core invoice header records, raw unstructured string text dumps, metadata timestamps, and pipeline validation flags (`Verified_Success` vs `Auto_Corrected_Success`).
* **`Bill_Items` (Child):** Tracks localized individual product line-items mapped to their parent invoice record via a secure Foreign Key cascade constraint.

## 🛠️ Software Stack & Core Modules
* **Backend Architecture:** Python 3.x, SQLite3
* **Web Serving UI Framework:** Flask (Responsive Dark-Themed Grid Layout)
* **Testing & Data Models:** Procedural automation logic evaluating line-by-line item consistency ($Quantity \times Unit\ Price = Line\ Total$).

## 🚀 How to Run the Web Dashboard Locally
1. Clone this repository to your machine.
2. Ensure Flask is installed via your environment (`pip install flask`).
3. Run the application startup script via terminal:
   ```bash
   python app.py
