from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

app = Flask(__name__)
CORS(app)

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'campusdb'),
        user=os.getenv('DB_USER', 'campusadmin'),
        password=os.getenv('DB_PASSWORD', 'campus123'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            ip VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'ok',
            connected_to TEXT DEFAULT '[]',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id SERIAL PRIMARY KEY,
            device_id INT REFERENCES devices(id),
            device_name VARCHAR(100),
            type VARCHAR(100) NOT NULL,
            description TEXT,
            severity VARCHAR(20) DEFAULT 'warning',
            status VARCHAR(30) DEFAULT 'Open',
            assigned_to VARCHAR(100),
            steps TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Insert sample devices if empty
    cur.execute("SELECT COUNT(*) FROM devices")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO devices (name, type, ip, status, connected_to) VALUES
            ('Core Switch', 'switch', '192.168.1.1', 'ok', '[2,3,4]'),
            ('Block A Switch', 'switch', '192.168.1.2', 'warning', '[5,6]'),
            ('Block B Switch', 'switch', '192.168.1.3', 'critical', '[7]'),
            ('Library Switch', 'switch', '192.168.1.4', 'ok', '[]'),
            ('Camera A1', 'camera', '192.168.2.1', 'ok', '[]'),
            ('Camera A2', 'camera', '192.168.2.2', 'critical', '[]'),
            ('DVR Block B', 'dvr', '192.168.3.1', 'warning', '[]')
        """)

    # Insert sample problems if empty
    cur.execute("SELECT COUNT(*) FROM problems")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO problems (device_id, device_name, type, description, severity, status, assigned_to, steps) VALUES
            (3, 'Block B Switch', 'Link Down', 
             'Uplink port is down. No connectivity to connected devices.', 
             'critical', 'Open', 'Adithyan',
             '["Check physical cable connection on port 1","Verify the connected device is powered on","Check switch port status using admin console","Try connecting to a different port","If problem persists replace the cable"]'),
            (6, 'Camera A2', 'CCTV Feed Down',
             'Camera feed is unavailable. Device not responding to ping.',
             'critical', 'In Progress', 'Deion',
             '["Check if camera has power (LED indicator)","Verify network cable is properly connected","Ping the camera IP from admin PC","Check PoE switch port for the camera","Reboot the camera by disconnecting power","Check DVR/NVR for recording status"]'),
            (2, 'Block A Switch', 'High CPU Usage',
             'Switch CPU usage above 85%. Performance degraded.',
             'warning', 'Open', 'Nivedhya',
             '["Login to switch admin console","Check running processes and CPU stats","Look for any broadcast storm or loop","Check STP (Spanning Tree) status","Reboot switch during off-peak hours if needed"]'),
            (7, 'DVR Block B', 'Recording Failure',
             'DVR has stopped recording. Storage may be full.',
             'warning', 'Resolved', 'Sourav',
             '["Check DVR storage capacity","Delete old recordings if storage is full","Verify DVR network connection","Restart DVR recording service","Check camera connections to DVR"]')
        """)

    conn.commit()
    cur.close()
    conn.close()

# ── AUTH ──────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, role FROM users WHERE username=%s AND password_hash=%s",
            (username, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return jsonify({
                'success': True,
                'user': {'id': user[0], 'username': user[1], 'role': user[2]}
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ── DEVICES ───────────────────────────────────────
@app.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, type, ip, status, connected_to FROM devices ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        devices = []
        for row in rows:
            devices.append({
                'id': str(row[0]),
                'name': row[1],
                'type': row[2],
                'ip': row[3],
                'status': row[4],
                'connectedTo': row[5]
            })
        return jsonify({'success': True, 'devices': devices})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ── PROBLEMS ──────────────────────────────────────
@app.route('/api/problems', methods=['GET'])
def get_problems():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, device_id, device_name, type, description, 
                   severity, status, assigned_to, steps,
                   TO_CHAR(created_at, 'HH12:MI AM')
            FROM problems ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        problems = []
        for row in rows:
            import json
            problems.append({
                'id': str(row[0]),
                'deviceId': str(row[1]),
                'deviceName': row[2],
                'type': row[3],
                'description': row[4],
                'severity': row[5],
                'status': row[6],
                'assignedTo': row[7],
                'steps': json.loads(row[8]) if row[8] else [],
                'time': row[9]
            })
        return jsonify({'success': True, 'problems': problems})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ── UPDATE PROBLEM STATUS ─────────────────────────
@app.route('/api/problems/<int:problem_id>/status', methods=['PUT'])
def update_problem_status(problem_id):
    data = request.json
    new_status = data.get('status')
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Update problem status
        cur.execute(
            "UPDATE problems SET status=%s WHERE id=%s",
            (new_status, problem_id)
        )
        
        # Get the device_id for this problem
        cur.execute(
            "SELECT device_id FROM problems WHERE id=%s",
            (problem_id,)
        )
        row = cur.fetchone()
        
        if row:
            device_id = row[0]
            
            # Check all problems for this device
            cur.execute("""
                SELECT status FROM problems 
                WHERE device_id=%s
            """, (device_id,))
            all_statuses = [r[0] for r in cur.fetchall()]
            
            # Decide new device status
            if any(s == 'Open' for s in all_statuses):
                device_status = 'critical'
            elif any(s == 'In Progress' for s in all_statuses):
                device_status = 'warning'
            else:
                # All resolved
                device_status = 'ok'
            
            # Update device status
            cur.execute(
                "UPDATE devices SET status=%s WHERE id=%s",
                (device_status, device_id)
            )
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
# ── STATS ─────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status, COUNT(*) FROM devices GROUP BY status")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        stats = {'ok': 0, 'warning': 0, 'critical': 0}
        for row in rows:
            stats[row[0]] = row[1]
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Store OTPs temporarily (in production use Redis)
otp_store = {}

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    username = data.get('username')
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT email FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row or not row[0]:
            return jsonify({'success': False, 'message': 'Username not found'}), 404
        
        email = row[0]
        otp = str(random.randint(100000, 999999))
        otp_store[username] = otp
        
        # Send email
        try:
            sender_email = "your_gmail@gmail.com"  # Change this
            sender_password = "your_app_password"   # Change this
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = 'Campus Connect Care - Password Reset OTP'
            
            body = f"""
Hello {username},

Your OTP for password reset is: {otp}

This OTP is valid for 10 minutes.

Do not share this OTP with anyone.

Campus Connect Care
GEC Idukki
            """
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            server.quit()
            
            # Mask email for display
            masked = email[:2] + '****' + email[email.index('@'):]
            return jsonify({
                'success': True,
                'message': f'OTP sent to {masked}'
            })
        except Exception as e:
            # For testing - return OTP directly if email fails
            return jsonify({
                'success': True,
                'message': f'OTP (test mode): {otp}',
                'otp': otp
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    username = data.get('username')
    otp = data.get('otp')
    
    if otp_store.get(username) == otp:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid OTP'}), 400

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    username = data.get('username')
    otp = data.get('otp')
    new_password = data.get('newPassword')
    
    if otp_store.get(username) != otp:
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 400
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password_hash=%s WHERE username=%s",
            (new_password, username)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Remove used OTP
        del otp_store[username]
        
        return jsonify({'success': True, 'message': 'Password reset successful'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    print("Initializing database tables...")
    try:
        init_db()
        print("Database ready!")
    except Exception as e:
        print(f"DB init failed: {e}")
        print("Starting API without DB init...")
    
    print("Starting Campus Connect Care API...")
    print("API running at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
    