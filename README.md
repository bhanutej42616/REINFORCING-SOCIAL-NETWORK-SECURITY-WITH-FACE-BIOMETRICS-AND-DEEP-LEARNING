# 🔐 Social Network Security with Face Recognition

A Flask-based web application that replaces traditional password login with **face recognition authentication**. Users register using email OTP verification, capture their face via webcam, and log in by simply showing their face — no password needed.

---

## ✨ Features

- 📧 Email OTP verification during registration
- 📸 Webcam-based face capture and detection
- 🧠 Face feature extraction using OpenCV Haar Cascades
- 🔒 Face-based login with Pearson correlation matching
- 🗄️ MySQL database for storing user data and face encodings
- 🎯 YOLOv8 (Ultralytics) integrated for object detection

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Computer Vision | OpenCV, YOLOv8 |
| Email | Flask-Mail (Gmail SMTP) |
| Database | MySQL, Flask-MySQLdb |
| Frontend | HTML, CSS, JavaScript |

---

## 📁 Project Structure

```
Social Network Sec/
├── main.py                  # Main Flask application
├── model.py                 # YOLOv8 model loader
├── requirements.txt         # Python dependencies
├── face_auth_db.sql         # MySQL database schema
├── yolov8n.pt               # YOLOv8 pre-trained weights
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── index.html
    ├── register.html
    ├── login.html
    └── dashboard.html
```

---

## ⚙️ How It Works

### Registration
1. User fills in their name, username, email, and date of birth
2. A 6-digit OTP is sent to the provided email
3. After OTP verification, the user captures their face via webcam
4. OpenCV detects the face, extracts a 128×128 pixel feature vector, and stores it in MySQL

### Login
1. User enters their registered email
2. User captures their face via webcam
3. The live face features are compared to stored features using **Pearson correlation**
4. If similarity exceeds the threshold (0.8), access is granted

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12
- MySQL Server
- A Gmail account with an [App Password](https://support.google.com/accounts/answer/185833)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/social-network-sec.git
   cd social-network-sec
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   mysql -u root -p < face_auth_db.sql
   ```

5. **Configure environment variables**

   Create a `.env` file in the root directory:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=face_auth_db
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_gmail_app_password
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

7. Open your browser and go to `http://127.0.0.1:5000`

---

## 📦 Requirements

```
python == 3.12
Flask == 3.0.2
Flask-Mail == 0.9.1
Flask-MySQLdb == 2.0.0
opencv-python == 4.9.0.80
ultralytics == 8.3.58
numpy == 1.26.4
```

---

## 📸 Screenshots

> _Add screenshots of the registration, face capture, and login pages here._

---

## ⚠️ Security Notes

- Never hardcode credentials in `main.py` — use environment variables or a `.env` file
- The face comparison uses pixel correlation, which may be sensitive to lighting and camera angle
- For production use, consider replacing the correlation method with a deep learning-based face embedding (e.g., `face_recognition` or `DeepFace`)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
