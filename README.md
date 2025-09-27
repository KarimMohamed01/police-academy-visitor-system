Visitor Management System for Police Academy
A Visitor Management System built with Python (Flask + PyQt6). The system allows visitors to check in via QR code using a local web form, with data stored in an SQLite database. Administrators can manage visitor records through a desktop interface, including search, view, and export to Excel. The entire system runs fully offline within a local network.

✨ Features
📝 Visitor Registration via QR code and local web form
💾 SQLite database for secure offline data storage
🖥️ Admin Desktop Interface (PyQt6) to manage records
🔍 Search & Filter visitor history
📊 Export to Excel for reports (via pandas)
🔐 Staff Management with roles & permissions
🌐 Runs offline in a local intranet environment

🛠️ Tech Stack
Frontend (Admin UI): PyQt6
Backend (Visitor Form): Flask
Database: SQLite
Utilities: qrcode, Pillow, pandas

📂 Project Structure
main.py                # Entry point for the application
academy_visitors.db    # SQLite database (auto-created)
templates/             # Flask HTML templates (for visitor form)
static/                # Static assets (if any: CSS, JS, QR images)
requirements.txt       # Dependencies for the project



⚙️ Installation
1. Clone the repository
git clone https://github.com/your-username/police-academy-visitor-system.git
cd police-academy-visitor-system



2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows



3. Install dependencies
pip install -r requirements.txt


▶️ Usage
1. Run the application
python main.py

3. Access the visitor form
Open your browser at: http://localhost:5000


3. Admin interface
The PyQt6 desktop window will open automatically, allowing you to:
Search visitors| View visitor details| Export records to Excel

📜 License
This project is licensed under the Encrypt Core – feel free to use and modify.
