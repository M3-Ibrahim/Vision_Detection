from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
from predict_video_realtime import Alert
import time
import secrets
import pickle
from tensorflow.keras.models import load_model

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder="Static/")
        self.app.config['SECRET_KEY'] = secrets.token_hex(16)
        self.socketio = SocketIO(self.app)

        self.IP = "rtsp://admin:ho@987654@192.168.88.232"
        self.PI = "rtsp://admin:ho@987654@192.168.88.235"

        self.model = load_model("Alert/videoClassification/model")
        self.lb = pickle.loads(open("Alert/videoClassification/label_bin", "rb").read())

        @self.app.route('/')
        def index():
            return render_template('Theft.html')

        @self.socketio.on('connect')
        def on_connect():
            thread1 = threading.Thread(target=self.fun)
            thread3 = threading.Thread(target=self.funct)

            thread1.start()
            thread3.start()

    def fun(self):
        while True:
            start_time = time.time()
            result = Alert.check(self.IP, self.model, self.lb)
            end_time = time.time()
            execution_time = end_time - start_time
            print("### ###")
            # Save the result to a text file
            with open('result1.txt', 'w') as file:
                file.write(f"Function 1 execution time: {execution_time:.4f} seconds. Result: {result}")

            # Read the saved result from the text file into another variable
            with open('result1.txt', 'r') as file:
                saved_result = file.read()

            self.socketio.emit('fun_result', saved_result)
            time.sleep(3)  # Update every 5 seconds

    def funct(self):
        while True:
            start_time = time.time()
            result = Alert.check(self.PI, self.model, self.lb)
            end_time = time.time()
            execution_time = end_time - start_time
            print("#### ####")
            # Save the result to a text file
            with open('result3.txt', 'w') as file:
                file.write(f"Function 3 execution time: {execution_time:.4f} seconds. Result: {result}")

            # Read the saved result from the text file into another variable
            with open('result3.txt', 'r') as file:
                saved_result = file.read()

            self.socketio.emit('funct_result', saved_result)
            time.sleep(3)  # Update every 5 seconds

if __name__ == '__main__':
    app_instance = FlaskApp()
    app_instance.socketio.run(app_instance.app)
