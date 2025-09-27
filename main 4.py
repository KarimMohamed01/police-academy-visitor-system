
import sys
import threading
import socket
import io
from datetime import datetime

from PyQt6 import QtWidgets, QtGui, QtCore
from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import qrcode
from PIL.ImageQt import ImageQt
import sqlite3
import pandas as pd
import os


DB_PATH = "academy_visitors.db"
DEFAULT_PORT = 5000


def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        national_id TEXT,
        phone TEXT,
        reason TEXT,
        submitted_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        national_id TEXT,
        phone TEXT,
        role TEXT,
        permissions TEXT
    )""")
    con.commit()
    con.close()

def insert_visitor(name, national_id, phone, reason):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO visitors (name,national_id,phone,reason,submitted_at) VALUES (?,?,?,?,?)",
                (name, national_id, phone, reason, now))
    con.commit()
    con.close()

def query_visitors(search=None):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    if search:
        like = f"%{search}%"
        cur.execute("SELECT id,name,national_id,phone,reason,submitted_at FROM visitors WHERE name LIKE ? OR national_id LIKE ?",
                    (like, like))
    else:
        cur.execute("SELECT id,name,national_id,phone,reason,submitted_at FROM visitors ORDER BY submitted_at DESC")
    rows = cur.fetchall()
    con.close()
    return rows

def export_visitors_to_excel(path):
    rows = query_visitors()
    df = pd.DataFrame(rows, columns=["id","name","national_id","phone","reason","submitted_at"])
    df.to_excel(path, index=False)


app = Flask(__name__)

VISIT_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <title>Visitor Check-in</title>
  <style>
    body {
      font-family: Tahoma, Arial, sans-serif;
      background: #f4f6f9;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }
    .form-container {
      background: #fff;
      padding: 25px 30px;
      border-radius: 12px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      width: 350px;
      text-align: center;
    }
    h2 {
      margin-bottom: 20px;
      color: #333;
    }
    label {
      display: block;
      margin-bottom: 15px;
      text-align: right;
    }
    input, textarea {
      width: 100%;
      padding: 10px;
      margin-top: 5px;
      border: 1px solid #ccc;
      border-radius: 8px;
      font-size: 14px;
    }
    textarea {
      resize: vertical;
      min-height: 70px;
    }
    button {
      background: #007bff;
      color: white;
      border: none;
      padding: 12px 18px;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
      transition: 0.3s;
      width: 100%;
    }
    button:hover {
      background: #0056b3;
    }
  </style>
  <script>
    function validateForm() {
      const name = document.getElementById('name').value.trim();
      const nid = document.getElementById('nid').value.trim();
      const phone = document.getElementById('phone').value.trim();

      // التحقق من الاسم (حروف ومسافات فقط)
      const nameRegex = /^[\u0621-\u064Aa-zA-Z ]+$/;
      if (!nameRegex.test(name)) {
        alert("❌ الاسم يجب أن يحتوي على حروف فقط (عربية أو إنجليزية).");
        return false;
      }

      // التحقق من رقم البطاقة
      if (nid.length !== 14) {
        alert("❌ يجب إدخال رقم البطاقة المكون من 14 رقم بالضبط.");
        return false;
      }

      // التحقق من رقم الموبايل
      if (phone.length !== 11) {
        alert("❌ يجب إدخال رقم التليفون المكون من 11 رقم بالضبط.");
        return false;
      }

      return true;
    }
  </script>
</head>
<body>
  <div class="form-container">
    <h2>تسجيل زيارة</h2>
    <form method="post" action="/submit" onsubmit="return validateForm()">
      <label>الاسم:
        <input id="name" name="name" required placeholder="اكتب اسمك هنا"
               oninput="this.value=this.value.replace(/[^\\u0621-\\u064Aa-zA-Z ]/g,'')">
      </label>
      <label>رقم البطاقة/الهوية:
        <input id="nid" name="national_id" required 
                placeholder="قم بإدخال رقم البطاقة المكون من 14 رقم"
                  maxlength="14"
                  oninput="this.value=this.value.replace(/[^0-9]/g,'').slice(0,14)">
      </label>
      <label>التليفون:
        <input id="phone" name="phone" required 
               placeholder="قم بإدخال رقم التليفون المكون من 11 رقم"
                maxlength="11"
            oninput="this.value=this.value.replace(/[^0-9]/g,'').slice(0,11)">
      </label>
      <label>سبب الزيارة:
        <textarea name="reason" placeholder="اختياري..."></textarea>
      </label>
      <button type="submit">إرسال</button>
    </form>
  </div>
</body>
</html>
"""






THANK_YOU = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <title>شكراً</title>
  <style>
    body {
      font-family: Tahoma, Arial, sans-serif;
      background: #f4f6f9;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }
    .thank-container {
      background: #fff;
      padding: 30px 40px;
      border-radius: 12px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      text-align: center;
      animation: fadeIn 1s ease-in-out;
    }
    h3 {
      margin-top: 20px;
      font-size: 20px;
      color: #333;
    }
    /* ✅ ستايل علامة الصح */
    .checkmark {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      display: block;
      stroke-width: 2;
      stroke: #28a745;
      stroke-miterlimit: 10;
      margin: 0 auto;
      box-shadow: inset 0px 0px 0px #28a745;
      animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both;
    }
    .checkmark__circle {
      stroke-dasharray: 166;
      stroke-dashoffset: 166;
      stroke-width: 4;
      stroke-miterlimit: 10;
      stroke: #28a745;
      fill: none;
      animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
    }
    .checkmark__check {
      transform-origin: 50% 50%;
      stroke-dasharray: 48;
      stroke-dashoffset: 48;
      stroke: #28a745;
      stroke-width: 4;
      animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
    }
    @keyframes stroke {
      100% { stroke-dashoffset: 0; }
    }
    @keyframes scale {
      0%, 100% { transform: none; }
      50% { transform: scale3d(1.1, 1.1, 1); }
    }
    @keyframes fill {
      100% { box-shadow: inset 0px 0px 0px 60px #fff; }
    }
  </style>
</head>
<body>
  <div class="thank-container">
    <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
      <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none"/>
      <path class="checkmark__check" fill="none" d="M14 27l7 7 16-16"/>
    </svg>
    <h3>تم تسجيل بياناتك. شكراً لزيارتك.</h3>
  </div>
</body>
</html>
"""



@app.route("/")
def index():
    return redirect(url_for('visit'))

@app.route("/visit")
def visit():
    
    return render_template_string(VISIT_TEMPLATE)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name","").strip()
    national_id = request.form.get("national_id","").strip()
    phone = request.form.get("phone","").strip()
    reason = request.form.get("reason","").strip()

    if not name or not national_id or not phone:
        return "Missing required fields", 400

    
    if not (national_id.isdigit() and len(national_id) == 14):
        return "الرقم القومي يجب أن يكون 14 رقم", 400
    if not (phone.isdigit() and len(phone) == 11):
        return "رقم التليفون يجب أن يكون 11 رقم", 400

    insert_visitor(name, national_id, phone, reason)
    return render_template_string(THANK_YOU)

@app.route("/api/visitors")
def api_visitors():
    rows = query_visitors()
    data = [dict(id=r[0], name=r[1], national_id=r[2], phone=r[3], reason=r[4], submitted_at=r[5]) for r in rows]
    return jsonify(data)


def get_local_ip():
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        
        s.connect(("192.168.1.100", 5000))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


server_thread = None
server_running = False

def run_flask_in_thread(host, port):
    
    app.run(host=host, port=port, threaded=True)

def start_server(host, port):
    global server_thread, server_running
    if server_running:
        return
    server_thread = threading.Thread(target=run_flask_in_thread, args=(host, port), daemon=True)
    server_thread.start()
    server_running = True

def stop_server():
    
    global server_running
    server_running = False
    


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Police Academy Visitor Manager")
        self.resize(900, 600)

        
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        
        top_row = QtWidgets.QHBoxLayout()
        self.ip_label = QtWidgets.QLabel("Host IP:")
        self.ip_value = QtWidgets.QLineEdit(get_local_ip())
        self.port_label = QtWidgets.QLabel("Port:")
        self.port_value = QtWidgets.QLineEdit(str(DEFAULT_PORT))
        self.start_btn = QtWidgets.QPushButton("Start Server")
        self.stop_btn = QtWidgets.QPushButton("Stop Server")
        self.stop_btn.setEnabled(False)  

        
        self.start_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        self.stop_btn.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")

        top_row.addWidget(self.ip_label)
        top_row.addWidget(self.ip_value)
        top_row.addWidget(self.port_label)
        top_row.addWidget(self.port_value)
        top_row.addWidget(self.start_btn)
        top_row.addWidget(self.stop_btn)
        layout.addLayout(top_row)

        
        qr_row = QtWidgets.QHBoxLayout()
        self.qr_label = QtWidgets.QLabel()
        self.qr_label.setFixedSize(200, 200)
        qr_controls = QtWidgets.QVBoxLayout()
        self.generate_qr_btn = QtWidgets.QPushButton("Generate QR for /visit")
        self.qr_url_label = QtWidgets.QLineEdit()
        self.save_qr_btn = QtWidgets.QPushButton("Save QR image")
        qr_controls.addWidget(self.generate_qr_btn)
        qr_controls.addWidget(self.qr_url_label)
        qr_controls.addWidget(self.save_qr_btn)
        qr_row.addWidget(self.qr_label)
        qr_row.addLayout(qr_controls)
        layout.addLayout(qr_row)

        
        search_row = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search by name or national id...")
        self.search_btn = QtWidgets.QPushButton("Search")
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.export_btn = QtWidgets.QPushButton("Export Excel")
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_btn)
        search_row.addWidget(self.refresh_btn)
        search_row.addWidget(self.export_btn)
        layout.addLayout(search_row)

        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "National ID", "Phone", "Reason", "Submitted At"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        
        self.start_btn.clicked.connect(self.on_start)
        self.stop_btn.clicked.connect(self.on_stop)
        self.generate_qr_btn.clicked.connect(self.on_generate_qr)
        self.save_qr_btn.clicked.connect(self.on_save_qr)
        self.refresh_btn.clicked.connect(self.load_table)
        self.search_btn.clicked.connect(self.on_search)
        self.export_btn.clicked.connect(self.on_export)

        
        self.current_qr_img = None
        self.load_table()

        
        self.statusBar().showMessage("جاهز للعمل ✅")

    def on_start(self):
        host = self.ip_value.text().strip() or "0.0.0.0"
        port = int(self.port_value.text().strip() or DEFAULT_PORT)
        start_server(host, port)

        QtWidgets.QMessageBox.information(self, "Server", f" Server started working on http://{host}:{port} ✅")
        self.statusBar().showMessage(f"السيرفر شغال على {host}:{port}")

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def on_stop(self):
        stop_server()

        QtWidgets.QMessageBox.warning(self, "Server", "Server stopped⛔")
        self.statusBar().showMessage("Server is turned off❌")

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_generate_qr(self):
        custom_hostname = "academy.local"
        port = self.port_value.text().strip() or str(DEFAULT_PORT)
        url = f"http://{self.ip_value.text()}:{self.port_value.text()}/visit"

        self.qr_url_label.setText(url)

        img = qrcode.make(url)
        from PIL import Image
        if not isinstance(img, Image.Image):
            img = img.get_image()

        qim = ImageQt(img).copy()
        pix = QtGui.QPixmap.fromImage(qim).scaled(
            200, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio
        )
        self.qr_label.setPixmap(pix)
        self.current_qr_img = img

    def on_save_qr(self):
        if self.current_qr_img is None:
            QtWidgets.QMessageBox.warning(self, "QR", "Generate a QR first.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save QR", "visitor_qr.png", "PNG Files (*.png)")
        if path:
            self.current_qr_img.save(path)
            QtWidgets.QMessageBox.information(self, "Saved", f"QR saved to {path}")

    def load_table(self, search=None):
        rows = query_visitors(search)
        self.table.setRowCount(0)
        for r in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for c, val in enumerate(r):
                it = QtWidgets.QTableWidgetItem(str(val) if val is not None else "")
                self.table.setItem(row_idx, c, it)

    def on_search(self):
        term = self.search_input.text().strip()
        self.load_table(search=term)

    def on_export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Excel", "visitors.xlsx", "Excel Files (*.xlsx)")
        if path:
            export_visitors_to_excel(path)
            QtWidgets.QMessageBox.information(self, "Export", f"Exported visitors to {path}")

    def load_table(self, search=None):
        rows = query_visitors(search)
        self.table.setRowCount(0)
        for r in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for c, val in enumerate(r):
                it = QtWidgets.QTableWidgetItem(str(val) if val is not None else "")
                self.table.setItem(row_idx, c, it)

    def on_search(self):
        term = self.search_input.text().strip()
        self.load_table(search=term)

    def on_export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Excel", "visitors.xlsx", "Excel Files (*.xlsx)")
        if path:
            export_visitors_to_excel(path)
            QtWidgets.QMessageBox.information(self, "Export", f"Exported visitors to {path}")

def main():
    init_db()
    app_qt = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app_qt.exec())

if __name__ == "__main__":
    main()
