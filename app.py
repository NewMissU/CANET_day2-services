import websockets
import asyncio # allow running and waiting for a response that come from server ไม่หยุดรอ
from dotenv import load_dotenv
import os
import psycopg2
import json

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

#connect to the server
async def listenToServer():
    url = "ws://technest.ddns.net:8001/ws" #address of websocket
    API_KEY = "5e11ba59b77f3aea462e303a9a7fe416"
    
    try:
        async with websockets.connect(url) as ws: # เชื่อม websocket
            await ws.send(API_KEY) # check authorize api
            msg = await ws.recv() #recv = recieve รับข้อความจาก server
            if(msg == "Unauthorized"):
                print(msg)
            elif(msg == "Connection authorized"):
                print(msg)
                while(True):
                # for i in range(5): 
                    data = await ws.recv() # return string
                    print(data)
                    print(f"Type of msg : {type(data)}")
                    data_dict = json.loads(data) # แปลง string เป็น dict
                    print(data_dict)
                    print(f"Type of msg_dict : {type(data_dict)}")
                   
                    
                #data_dict = { --> dict ซ้อนกัน
                    #     "Energy Consumption":{
                    #         "Power":98.03944744405663
                    #     },
                    #     "Voltage":{
                    #         "L1-GND":226.2083319793826,
                    #         "L2-GND":228.83464577107483,
                    #         "L3-GND":234.72285235017273
                    #     },
                    #     "Pressure":19.870442829111305,
                    #     "Force":30.099099141627782,
                    #     "Cycle Count":18138,
                    #     "Position of the Punch":70.88454303171552
                # }

                    # เข้าถึง dictionary แรก 'Energy Consumption'
                    energy_consumption = data_dict['Energy Consumption']
                    # จากนั้นเข้าถึง key 'Power' ใน dictionary ซ้อนกัน
                    power_value = energy_consumption['Power']
                    
                    voltage = data_dict['Voltage']
                    l1_voltage = voltage['L1-GND']
                    l2_voltage = voltage['L2-GND']
                    l3_voltage = voltage['L3-GND']
                    
                    pressure = data_dict['Pressure']
                    force = data_dict['Force']
                    cycle_count = data_dict['Cycle Count']
                    position_of_the_punch = data_dict['Position of the Punch']
                    
                    # แสดงผล
                    print("Energy Consumption => Power:", power_value)  # Output: 19.405914942567914
                    print(type(power_value))
                    print("Voltage => L1-GND:", l1_voltage)  # Output: 19.405914942567914
                    print(type(l1_voltage))
                    print("Voltage => L2-GND:", l2_voltage)  # Output: 19.405914942567914
                    print(type(l2_voltage))
                    print("Voltage => L3-GND:", l3_voltage)  # Output: 19.405914942567914
                    print(type(l3_voltage))
                    print("Pressure:", pressure)  # Output: 19.405914942567914
                    print("Force:", force)        # Output: 30.533170000824647
                    print("Cycle Count:", cycle_count)  # Output: 4805
                    print("Position of the Punch:", position_of_the_punch)  # Output: 179.9575774853343
                    print("------------------------------------------------------")
                    
                    # คำสั่ง SQL สำหรับการสร้างตาราง (ถ้ายังไม่เคยสร้าง)
                    create_table_query = """
                    CREATE TABLE IF NOT EXISTS machine_data (
                        id SERIAL PRIMARY KEY,
                        energy_consumption_power NUMERIC(20, 14),
                        voltage_l1_gnd NUMERIC(20, 14),
                        voltage_l2_gnd NUMERIC(20, 14),
                        voltage_l3_gnd NUMERIC(20, 14),
                        pressure NUMERIC(20, 14),
                        force NUMERIC(20, 15),
                        cycle_count INTEGER,
                        position_of_the_punch NUMERIC(20, 14)
                    );
                    """
                    
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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """
                    
                    try:
                        with conn: # ทำลง database ต่อ
                            with conn.cursor() as cur: # Open a cursor to perform database operations
                                cur.execute(create_table_query) #   create table ถ้ายังไม่มี table
                                #Insert data into database
                                cur.execute(insert_query, (power_value,l1_voltage,l2_voltage,l3_voltage,pressure,force,cycle_count,position_of_the_punch))
                    except Exception as e:
                        print(f"An error occurred: {e}")
    except websockets.exceptions.WebSocketException as e:
        print(f"Error: {e}")  # จัดการกับข้อผิดพลาดจาก WebSocket
        
asyncio.get_event_loop().run_until_complete(listenToServer()) #event take the execution of this program
# run listenToServer() asynchronous , it will wait until everything is complete