from flask import Flask,request,jsonify,make_response,abort
import jwt
from datetime import datetime, timedelta # set expiration time for token
from functools import wraps
import uuid
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras

load_dotenv()

#Database connection parameter
DB_USER = os.getenv("DB_USER") # ดึงข้อมูลจาก .env มาใช้งาน
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")  # ค่าเริ่มต้นคือ localhost
DB_PORT = os.getenv("DB_PORT", "5433")

print("Username : " , DB_USER)
print("Password : " , DB_PASSWORD)
print("DatabaseName : " , DB_NAME)
print("Host : " , DB_HOST)
print("Port : " , DB_PORT)

#connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname = DB_NAME,
    user = DB_USER,
    password = DB_PASSWORD,
    host = DB_HOST,
    port = DB_PORT,
)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# การกำหนด cursor_factory เป็น psycopg2.extras.DictCursor หมายความว่า cursor ที่สร้างขึ้นจะทำงานในลักษณะพิเศษ 
# โดยจะคืนค่าผลลัพธ์เป็น dictionary แทนการคืนค่าเป็น tuple
# ใน dictionary แต่ละคีย์จะเป็นชื่อของคอลัมน์ในผลลัพธ์ และค่าของคีย์จะเป็นข้อมูลที่ตรงกับคอลัมน์นั้นในแถว (row) ที่ดึงมา


app = Flask(__name__)
app.config['SECRET_KEY'] = 'e6a22d50-27da-4c3b-b32b-a7d2c499561b'

# Decorator to check JWT
# def token_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         token = None
#         if 'Authorization' in request.headers:
#             token = request.headers['Authorization'].split(" ")[1]  # Get token from Authorization header

#         if not token:
#             return jsonify({'message': 'Token is missing!'}), 403

#         try:
#             # Decode token using SECRET_KEY
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
#             current_user = data['user_id']
#         except jwt.ExpiredSignatureError:
#             return jsonify({'message': 'Token has expired!'}), 403
#         except jwt.InvalidTokenError:
#             return jsonify({'message': 'Invalid token!'}), 403
#         except Exception as e:
#             return jsonify({'message': str(e)}), 500

#         return f(current_user, *args, **kwargs)
#     return decorated_function

@app.route('/')
def index():
    unique_id = uuid.uuid4()
    return f"""<h1>JWT API</h1>
        <p>Your unique ID: {unique_id}</p>"""
        
# Login route to get JWT token
# @app.route('/login', methods=['POST'])
# def login():
#     auth = request.json
#     if not auth or not auth.get('username') or not auth.get('password'):
#         return jsonify({'message': 'Could not verify'}), 401

#     username = auth['username']
#     password = auth['password']

#     # For simplicity, let's assume a static user (you can replace this with a DB query)
#     if username == 'admin' and password == 'password':  # Example of hardcoded credentials
#         token = jwt.encode(
#             {'user_id': username, 
#              'exp': str(datetime.utcnow() + timedelta(seconds=180))}  # token will expire in 1 hour
#             # app.config['SECRET_KEY'],
#             # algorithm="HS256"
#         )
#         app.config['SECRET_KEY']
#         return jsonify({'token': token.decode('utf-8')})
#     else: 
#         return make_response('Unable to verify', 403, {'WWW-Authenticate' : 'Basic realm:"Athentication Failed!'})

# Route สำหรับการเข้าสู่ระบบเพื่อรับ JWT token
# @app.route('/login', methods=['POST'])
# def login():
#     auth = request.json
#     if not auth or not auth.get('username') or not auth.get('password'):
#         return jsonify({'message': 'Could not verify'}), 401

#     username = auth['username']
#     password = auth['password']

#     if username == 'admin' and password == 'password':  # Example of hardcoded credentials
#         token = jwt.encode(
#             {'user_id': username, 'exp': datetime.utcnow() + timedelta(hours=1)},
#             app.config['SECRET_KEY'],
#             algorithm="HS256"
#         ).decode('utf-8')  # Convert to string before returning
#         return jsonify({'token': token})

#     return jsonify({'message': 'Could not verify'}), 401

@app.route('/data', methods=['GET']) 
def get_data():
    cur.execute("SELECT * FROM machine_data")
    
    # Fetch all results
    rows = cur.fetchall()
    # Get the column names
    # columns = [desc[0] for desc in cur.description]
    # print(columns)
    # Convert each row into a dictionary with column names as keys
    # machines = [dict(zip(columns, row)) for row in rows] # zip() เพื่อจับคู่ชื่อคอลัมน์จาก columns กับค่าจากแต่ละแถวใน rows
    machines = [dict(row) for row in rows]
    # print(machines)
    return jsonify(machines), 200 
# หากคอลัมน์ในตาราง machine_data ถูกกำหนดเป็น NUMERIC(20, 14) ข้อมูลที่ถูกดึงมาจะมีลักษณะเป็น Decimal ของ Python รองรับการคำนวณเลขทศนิยมที่มีความแม่นยำสูง
# เนื่องจาก Decimal ไม่สามารถแปลงเป็น JSON ได้โดยตรง (JSON รองรับเฉพาะ int, float, str, bool, list, และ dict)   
# วิธีแก้ไข: เพื่อให้ Flask สามารถส่งข้อมูล Decimal ได้ในรูปแบบที่ถูกต้องใน JSON response, คุณสามารถแปลงค่าจาก Decimal เป็น float หรือ str ก่อนที่จะใช้ jsonify ดังนี้:
    
@app.route('/data', methods=['POST'])
def add_data():
    data = request.get_json()
    
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    
    cycle_count = data['cycle_count']
    energy_consumption_power = data['energy_consumption_power']
    force = data['force']
    position_of_the_punch = data['position_of_the_punch']
    pressure = data['pressure']
    voltage_l1_gnd = data['voltage_l1_gnd']
    voltage_l2_gnd = data['voltage_l2_gnd']
    voltage_l3_gnd = data['voltage_l3_gnd']
    
    if None in (cycle_count, energy_consumption_power, force, position_of_the_punch, pressure, voltage_l1_gnd, voltage_l2_gnd, voltage_l3_gnd):
        return jsonify({"error": "Missing required data fields"}), 400
    
    try:
        insert_query = """
        INSERT INTO machine_data(
            energy_consumption_power,
            voltage_l1_gnd,
            voltage_l2_gnd,
            voltage_l3_gnd,
            pressure,
            force,
            cycle_count,
            position_of_the_punch
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *;
        """
        cur.execute(insert_query, (energy_consumption_power,voltage_l1_gnd,voltage_l2_gnd,voltage_l3_gnd,pressure,force,cycle_count,position_of_the_punch))
        new_data = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        abort(500, description="เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์")
    return jsonify(dict(new_data)),201
    
@app.route('/data/<int:id>', methods=['PUT'])
def update_data(id):
    data = request.get_json()
    
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    
    cycle_count = data['cycle_count']
    energy_consumption_power = data['energy_consumption_power']
    force = data['force']
    position_of_the_punch = data['position_of_the_punch']
    pressure = data['pressure']
    voltage_l1_gnd = data['voltage_l1_gnd']
    voltage_l2_gnd = data['voltage_l2_gnd']
    voltage_l3_gnd = data['voltage_l3_gnd']
    
    if None in (cycle_count, energy_consumption_power, force, position_of_the_punch, pressure, voltage_l1_gnd, voltage_l2_gnd, voltage_l3_gnd):
        return jsonify({"error": "Missing required data fields"}), 400
    
    try:
        cur.execute('SELECT * FROM machine_data WHERE id = %s', (id,))
        change_thisdata = cur.fetchone()
        if change_thisdata == None:
            conn.rollback()
            abort(404, description="ไม่พบผู้ใช้")
        cur.execute(
            """UPDATE machine_data SET energy_consumption_power = %s, voltage_l1_gnd = %s, voltage_l2_gnd = %s, 
            voltage_l3_gnd = %s, pressure = %s, force = %s, cycle_count = %s, position_of_the_punch = %s WHERE id = %s RETURNING *""",
            (energy_consumption_power, voltage_l1_gnd, voltage_l2_gnd, voltage_l3_gnd, pressure, force, cycle_count, position_of_the_punch, id)
        )
        updated_data = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        abort(500, description="เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์")
    return jsonify(dict(updated_data)),200
    
@app.route('/data/<int:id>', methods=['DELETE'])
def delete_data(id): 
    try:
        cur.execute('SELECT * FROM machine_data WHERE id = %s', (id,))
        change_thisdata = cur.fetchone()
        if change_thisdata == None:
            conn.rollback()
            abort(404, description="ไม่พบผู้ใช้")
        cur.execute('DELETE FROM machine_data WHERE id = %s', (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        abort(500, description="เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์")
    return jsonify({"message": "Delete successfully!"}),200
    
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)