# Visitor Management System for Police Academy
A Visitor Management System built with Python (Flask + PyQt6). The system allows visitors to check in via QR code using a local web form, with data stored in an SQLite database. Administrators can manage visitor records through a desktop interface, including search, view, and export to Excel. The entire system runs fully offline within a local network.

# ✨ Features
📝 Visitor Registration via QR code and local web form<br>
💾 SQLite database for secure offline data storage<br>
🖥️ Admin Desktop Interface (PyQt6) to manage records<br>
🔍 Search & Filter visitor history<br>
📊 Export to Excel for reports (via pandas)<br>
🔐 Staff Management with roles & permissions<br>
🌐 Runs offline in a local intranet environment<br>

# 🛠️ Tech Stack
Frontend (Admin UI): PyQt6<br>
Backend (Visitor Form): Flask<br>
Database: SQLite<br>
Utilities: qrcode, Pillow, pandas<br>

# 📂 Project Structure
main.py                ```# Entry point for the application```<br>
academy_visitors.db    ```# SQLite database (auto-created)```<br>
templates/             ```# Flask HTML templates (for visitor form)```<br>
static/                ```# Static assets (if any: CSS, JS, QR images)```<br>
requirements.txt       ```# Dependencies for the project```<br>



# ⚙️ Installation
1. Clone the repository<br>
```git clone https://github.com/your-username/police-academy-visitor-system.git```<br>
```cd police-academy-visitor-system```<br>



2. Create a virtual environment (recommended)<br>
```python -m venv venv```<br>
```source venv/bin/activate```   # On Linux/Mac<br>
```venv\Scripts\activate ```     # On Windows<br>



3. Install dependencies<br>
```pip install -r requirements.txt```<br>


# ▶️ Usage
1. Run the application<br>
```python main.py```<br>

3. Access the visitor form<br>
Open your browser at: http://localhost:5000<br>


3. Admin interface<br>
The PyQt6 desktop window will open automatically, allowing you to: Search visitors| View visitor details| Export records to Excel<br>

# 📸 Screenshots

<img width="672" height="470" alt="Screenshot 2025-09-27 at 6 40 13 PM" src="https://github.com/user-attachments/assets/8f8c10ca-860d-4c0e-aa01-94482ac9b904" />





# 📜 License
This project is licensed under the Encrypt Core – feel free to use and modify.<br>
