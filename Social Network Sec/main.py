from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from ultralytics import YOLO
import cv2
import numpy as np
import os
import random
import string
import base64

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'face_auth_db'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pallavigonepalli55@gmail.com'
app.config['MAIL_PASSWORD'] = 'pstu ueqi oukd qwje'

mail = Mail(app)
mysql = MySQL(app)
yolo_model = YOLO('yolov8n.pt')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))
def send_otp_email(email, otp):
    msg = Message('OTP Verification',
                  sender='pallavigonepalli55@gmail.com',
                  recipients=[email])
    msg.body = f'Your OTP for registration is: {otp}'
    mail.send(msg)
def extract_face_features(image_array):
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None, None, "No face detected"
    if len(faces) > 1:
        return None, None, "Multiple faces detected"
    (x, y, w, h) = faces[0]
    cv2.rectangle(image_array, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(image_array, "Face Detected", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    face_roi = gray[y:y + h, x:x + w]
    face_roi = cv2.resize(face_roi, (128, 128))
    face_roi = face_roi.astype('float32') / 255.0
    face_features = face_roi.flatten()
    return face_features, image_array, None
def compare_faces(face1, face2, threshold=0.8):
    correlation = np.corrcoef(face1, face2)[0, 1]
    return correlation > threshold

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-email', methods=['POST'])
def check_email():
    email = request.form['email']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cur.fetchone()
    cur.close()
    if user:
        session['login_email'] = email
        return jsonify({'exists': True})
    return jsonify({'exists': False})
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        dob = request.form.get('dob')

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s OR username = %s', (email, username))
        user = cur.fetchone()
        cur.close()

        if user:
            return jsonify({'error': 'Email or username already registered'})

        session['registration_data'] = {
            'email': email,
            'fullname': fullname,
            'username': username,
            'dob': dob
        }

        otp = generate_otp()
        session['otp'] = otp
        send_otp_email(email, otp)

        return jsonify({'message': 'OTP sent successfully'})

    return render_template('register.html')


@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    submitted_otp = request.form['otp']
    if submitted_otp == session.get('otp'):
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid OTP'})


@app.route('/capture-face', methods=['POST'])
def capture_face():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'})

    if 'registration_data' not in session:
        return jsonify({'error': 'Registration data not found'})

    registration_data = session['registration_data']
    print(registration_data)
    required_fields = ['email', 'username', 'fullname', 'dob']
    if not all(field in registration_data for field in required_fields):
        return jsonify({'error': 'Missing registration data'})

    image_file = request.files['image']
    image_array = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)

    face_features, processed_image, error = extract_face_features(image_array)

    if error:
        return jsonify({'error': error})

    _, buffer = cv2.imencode('.jpg', processed_image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    try:
        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO users (email, username, fullname, dob, face_encoding) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            registration_data['email'],
            registration_data['username'],
            registration_data['fullname'],
            registration_data['dob'],
            face_features.tobytes()
        ))

        mysql.connection.commit()
        cur.close()
        session.pop('registration_data', None)

        return jsonify({'success': True, 'image': encoded_image})

    except Exception as e:
        if cur:
            cur.close()
        return jsonify({'error': f'Database error: {str(e)}'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'login_email' not in session:
            return jsonify({'error': 'Email not verified'})

        image_file = request.files['image']
        image_array = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)

        login_face_features, processed_image, error = extract_face_features(image_array)

        if error:
            return jsonify({'error': error})

        cur = mysql.connection.cursor()
        cur.execute('SELECT face_encoding FROM users WHERE email = %s', (session['login_email'],))
        result = cur.fetchone()
        cur.close()

        if not result:
            return jsonify({'error': 'User not found'})

        stored_features = np.frombuffer(result[0], dtype=np.float32)

        _, buffer = cv2.imencode('.jpg', processed_image)
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        if compare_faces(stored_features, login_face_features):
            session['user_email'] = session['login_email']
            return jsonify({'success': True, 'image': encoded_image})

        return jsonify({'error': 'Authentication failed', 'image': encoded_image})

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)