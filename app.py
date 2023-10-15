import json
import threading
import queue
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import cv2
import secrets
import concurrent.futures
import datetime
import pickle
from tensorflow.keras.models import load_model
from predict_video_realtime import Alert  # Import your alert module with check_camera function

app = Flask(__name__, template_folder="template")
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app)

total_count = []  # Initialize this list
timeStamp = []  # Initialize this list

# # cap = BL_VideoCapture('rtsp://admin:ho@987654@192.168.88.232')
IP1 = 'rtsp://admin:ho@987654@192.168.88.235'
IP2 = 'rtsp://admin:ho@987654@192.168.88.232'

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/person_up_down")
def person_up_down():
    # Replace this with your actual data retrieval logic
    data = [
        {"up": 10, "down": 5},
        {"up": 8, "down": 4}
    ]
    return jsonify(data)

@app.route("/Theft")
def theft():
    model = load_model("Alert/videoClassification/model")
    lb = pickle.loads(open("Alert/videoClassification/label_bin", "rb").read())

    def check_camera(IP, model, lb):
        try:
            result = Alert.check(IP, model, lb)
            return result
        except Exception as e:
            print(f"An error occurred in check_camera: {e}")
            return None

    cam1 = None
    cam2 = None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the camera checks as concurrent tasks
        cam1_future = executor.submit(check_camera, IP1, model, lb)
        cam2_future = executor.submit(check_camera, IP2, model, lb)

    # Get the results of the concurrent tasks
    cam1 = cam1_future.result()
    cam2 = cam2_future.result()

    response_data = {
        "Cam1": cam1
    }
    return jsonify(response_data)
    # return render_template("index.html",Cam1=cam1)

@app.route("/value")
def get_value():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    timeStamp.append(current_time)
    if len(timeStamp) == 6:
        timeStamp.pop(0)

    if len(total_count) == 6:
        total_count.pop(0)

    count = [{
        'id': total_count[-5:],
        'time': timeStamp
    }]

    return jsonify(count)

if __name__ == "__main__":
    app.run(debug=True)  