from flask import Flask, render_template, Response, request, json, jsonify, redirect, url_for, session
import cv2
import pickle
import cvzone
import numpy as np
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
import secrets
import os
from flask_session import Session
from decimal import Decimal

# Flask
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.secret_key = os.urandom(16)
# app.secret_key = secrets.token_hex(16)
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SECRET_KEY'] = 'adcfd45gft6tyhkm'
# print('HERE <<<<', app.config['SECRET_KEY'])
# Session(app)
# SESSION_TYPE = "filesystem"
# app.config.from_object(__name__)
# Session(app)
print("Shubham Singh-----",app.secret_key)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////mydb.db'
# db = SQLAlchemy(app)
# with app.app_context():
#     db.create_all()

# Capture Video
# cap = cv2.VideoCapture("carPark.mp4")
cap = cv2.imread('image10.jpg')
# cap=cv2.VideoCapture(0)

# Detect parking space
def generate_frames():
    while True:

        # success, img = cap.read()
        img = cap
        success = True
        

        if not success:
            break
        else:
            with open('CarParkPos_image10', 'rb') as f:
                posList = pickle.load(f)

            def checkParkingSpace(imgPro):
                
                spaceCounter = 0

                for i in range(0, len(posList), 2):
                    x1, x2 = posList[i]
                    x3, x4 = posList[i + 1]
                    width = abs((x3 - x1))
                    height = abs((x4 - x2))
                    # width = (x3 - x1)
                    # height = (x2 - x4)
                    pos = (x1, x2)

                    x, y = pos

                    imgCrop = imgPro[x2:x4, x1:x3]

                    # cv2.imshow(str(x * y), imgCrop)
                    count = cv2.countNonZero(imgCrop)
                    # print("shubham---", y + height, x + width,count)

                    if count < 1000:
                        color = (0, 255, 0)
                        thickness = 5
                        spaceCounter += 1
                    else:
                        color = (0, 0, 255)
                        thickness = 2

                    cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)

                    cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                                    thickness=2, offset=0, colorR=color)

                    cvzone.putTextRect(img, f'Free: {spaceCounter}/{int(len(posList)/2)}', (100, 50), scale=3,
                                    thickness=5, offset=20, colorR=(0, 200, 0))

                
            while True:

                img = cap
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
                imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY_INV, 25, 16)
                imgMedian = cv2.medianBlur(imgThreshold, 5)
                kernel = np.ones((3, 3), np.uint8)
                imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

                checkParkingSpace(imgDilate)
                
                ret, buffer = cv2.imencode('.jpg', img)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

app = Flask(__name__)

# Database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'parkinggarage'


mysql = MySQL(app)






app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# registration page route
@app.route('/', methods=['GET', 'POST'])
def get_data():
    # session['key'] = 'value12345678901'
    print("@@@@@@@@@@@@@---------",app.secret_key) 
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        vehicle_number = request.form['vehicle-number']
        balance = 0.0
        print("@@@@@!!!!!!!!!!!!!$$$$$$$^^^^^^^^******@@@@@@@")
        # insert user data into the database
        cursor = mysql.connection.cursor()
        cursor.execute(
            f"""INSERT INTO billingtable (name, email, password, balance, vehicalNumber, login) VALUES ('{name}', '{email}', '{password}', '{balance}', '{vehicle_number}', now());""")
        mysql.connection.commit()
        cursor.close()
        # session['email'] = email
        
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM billingtable WHERE email = '{email}'")
        user_data = cursor.fetchone()
        session['user_name'] = user_data[1]
        session['email_id'] = user_data[2]
        session['vehicle_number'] = user_data[3]
        session['balance'] = user_data[4]
        cursor.close()
        print("@@@@@@@@@@@@@@@@@@",session['vehicle_number'])
        # return redirect(url_for('dashboard'))
        return render_template('dashboard.html')
    return render_template('index.html')

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP--",app.secret_key)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # check if the email and password match with the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM billingtable WHERE email = %s AND password = %s", (email, password))

        # cursor = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        if user:
            # session['email'] = email
            cursor = mysql.connection.cursor()
            cursor.execute(f"SELECT * FROM billingtable WHERE email = '{email}'")
            user_data = cursor.fetchone()
            session['user_name'] = user_data[1]
            session['email_id'] = user_data[2]
            session['vehicle_number'] = user_data[3]
            session['balance'] = user_data[4]
            cursor.close()
            return render_template('dashboard.html')
            # return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error='Invalid email or password')
    return render_template('index.html')

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# dashboard page route
@app.route('/dashboard')
def dashboard():
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",app.secret_key)
    if 'email_id' in session:
        # retrieve user data from the database
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",session['email_id'])
        email = session['email_id']
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM billingtable WHERE email = '{email}'")
        user_data = cursor.fetchone()
        session['user_name'] = user_data[1]
        session['email_id'] = user_data[2]
        session['vehicle_number'] = user_data[3]
        session['balance'] = user_data[4]
        cursor.close()
        return render_template('dashboard.html')
    else:
        return render_template('index.html')

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/add_funds', methods=['GET', 'POST'])
def add_funds():
    print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
    if 'email_id' in session:
        if request.method == 'POST':
            print("}}}}}}}}")
            amount = float(request.form['amount'])
            amount_decimal = Decimal(str(amount))
            print("AAAAAAAAAAAAAAAAAAAAAAAAAA++++",amount)
            email = session['email_id']
            # retrieve user data from the database
            cursor = mysql.connection.cursor()
            cursor.execute(f"SELECT * FROM billingtable WHERE email = '{email}'")
            user_data = cursor.fetchone()
            session['user_name'] = user_data[1]
            session['email_id'] = user_data[2]
            session['vehicle_number'] = user_data[3]
            session['balance'] = user_data[4]
            upadated_amount = user_data[4] + amount_decimal
            cursor.close()
            print("user_data[4]----------",upadated_amount)
            # cursor.close()
            # cursor = conn.execute("SELECT * FROM users WHERE email = ?", (session['email'],))
            cursor = mysql.connection.cursor()
            query = "UPDATE billingtable SET balance = %s WHERE email = %s"
            params = (user_data[4]+amount_decimal, session['email_id'])
            print("Query:", query)
            print("Params:", params)
            cursor.execute(query, params)
            mysql.connection.commit()
            cursor.close()
            # update user balance in the database
            # cursor.execute("UPDATE billingtable SET balance = %s WHERE email = %s", (upadated_amount, session['email_id']))
            # conn.execute("UPDATE users SET balance = ? WHERE email = ?", (user[4]+amount, session['email']))
            # conn.commit()
            return redirect(url_for('dashboard'))
        return render_template('add_funds.html')
    else:
        return redirect(url_for('login'))


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# logout page route
@app.route('/logout')
def logout():
    session.pop('email_id', None)
    # return redirect(url_for('index.html'))
    return render_template("index.html")

# @app.route('/userInfo')
# def userInfo():
#     session.pop('email', None)
#     return redirect(url_for('home'))

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
@app.route('/homePage')
def homePage():
    return render_template("index.html")

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# Book Parking Space
@app.route('/bookingSuccess',methods=['GET', 'POST'])
def bookingSuccess():
    if request.method == 'POST':
        name = session['user_name']
        email = session['email_id']
        vehicleNumber = request.form['vehicleNumber']
        vehicleFlag = 0
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            f"""INSERT INTO bookingtable (name, email, vehicleNo, vehicleFlag, bookingTime) VALUES ('{name}', '{email}', '{vehicleNumber}', '{vehicleFlag}', now());""")
        mysql.connection.commit()
        cursor.close()
        
        return render_template("index.html")
    return render_template("index.html")




app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# Book Parking Space
@app.route('/bookParkingSpace')
def bookParkingSpace():
    if 'email_id' in session :
        return render_template("bookingform.html")
    return render_template("index.html")



# Help Desk Page

@app.route('/helpDesk')
def helpDesk():
    return render_template('helpDesk.html')

# About Us Page

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

# Parking Space Page

@app.route('/parking')
def parking():
    return render_template('parking.html')

# Stream video

@app.route('/parking/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Public Amenities Page

@app.route('/publicAmenities')
def publicAmentites():
    return render_template('PublicAmenitiesFirst.html')

# Parking Fees Page

@app.route('/parkingFees')
def get_time():
    mycursor = mysql.connection.cursor()
    mycursor.execute(
        "SELECT loginTime FROM registration ORDER BY loginTime DESC LIMIT 1")
    print("@@@@@@@@@@@@@@@@**************************************@@")
    myresult = mycursor.fetchall()
    print("$$$$$$$$$$$$$$$$$$$$$$$$",myresult)
    timestamps = []
    
    for r in myresult:
        timestamps.append(r[0])
    
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    timestamps_ = timestamps[0]
    currenttime = datetime.now()
    duration = currenttime-timestamps_
    d_secs = duration.total_seconds()
    d_hrs = d_secs//(60*60)
    if d_hrs <= 1:
        fees = """You've parked for less than or equal to an hour"""
        fee = "Rs. 10"
    elif d_hrs > 1:
        fee = f"""Rs. {10+((d_hrs-1)*5)}"""
        fees = f"You've parked for {d_hrs} hours"
    feeshtml = f'''
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

    <title>Parking Fees</title>
    </head>
    <body class="bg-dark" style="margin-top: 20vh;">
    <div class="card text-center text-dark bg-light" >
        <div class="card-header">
        Parking Ticket
        </div>
        <div class="card-body">
        <h2 class="card-title">{ fees }</h2>
        <h1 class="card-title">To Pay : { fee }</h1>
        <div class="container border-top border-bottom mt-4 mb-2 py-2">
            <h5 class="card-text text-muted">Summary</h5>
            <p class="card-text">Login Time : { timestamps_ }</p>
            <p class="card-text">Current Time : { currenttime }</p>
            <p class="card-text">Duration : { d_hrs } hours</p>
        </div>
        </div>
        <div class="card-footer text-muted">
        Thanks for using Parking Garage!
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
    </body>
</html>

'''
    with open("templates/fees.html", "w") as f:
        f.write(feeshtml)

    return render_template("fees.html")


# Driver code
if __name__ == "__main__":
    # sess = Session()
    # app.secret_key = 'super secret key'
    # app.config['SESSION_TYPE'] = 'filesystem'
    # sess.init_app(app)
    # app.secret_key = secrets.token_hex(16)
    app.run(debug=True)
