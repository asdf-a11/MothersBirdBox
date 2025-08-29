import traceback
try:
    from flask import Flask, render_template, Response, request, jsonify
    import io
    from PIL import Image
    import RPi.GPIO as GPIO
    import time
    import datetime
    from threading import Thread
    print("Importing camera modual")
    from picamera2 import Picamera2

    #GPIO mode init
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    #list of all ir LED pins
    ledPinList = [5,6]
    #Allow for writing to GPIO pins
    for p in ledPinList:
        GPIO.setup(p,GPIO.OUT)
    #Amount of time since server has sent data to client
    timeOfLastSend = time.time()
    #
    DISCONNECT_THRESH = 1 * 60
    #
    clientIsConnected = False

    def TurnOffLeds():
        for pin in ledPinList:
            GPIO.output(pin,GPIO.LOW)
    def TurnOnLeds():
        for pin in ledPinList:
            GPIO.output(pin,GPIO.HIGH)
    def CheckClientDisconnect():
        global clientIsConnected
        while True:
            print(time.time() - timeOfLastSend)
            if time.time() - timeOfLastSend > DISCONNECT_THRESH and clientIsConnected:
                print("Client has disconnected stopping cam and turning off leds at ", datetime.datetime.now().time())
                cam.Close()
                TurnOffLeds()
                clientIsConnected = False
            time.sleep(60)

    print("Starting detecting disconnected client thread")
    turnOffLedsThread = Thread(target=CheckClientDisconnect)  
    turnOffLedsThread.start()  
    

    app = Flask(__name__)

    class Camera():
        def __init__(self): 
            self.cam = Picamera2()
            self.cam.stop()
            self.cam.configure(
                self.cam.create_still_configuration(main={"size": (1280,720)})
            )
            self.cam.set_controls({
                "AfMode": 2,
                "AfTrigger": 0  # Optional: triggers the autofocus cycle
            })
            self.cam.start()
            self.isClosed = False
        def GetFrame(self):
            if self.isClosed:
                raise Exception("Trying to use camera even though it has been closed")
            # Capture as RGB array
            array = self.cam.capture_array()
            # Convert to JPEG bytes
            image = Image.fromarray(array)
            jpeg_io = io.BytesIO()
            image.save(jpeg_io, format="JPEG")
            return jpeg_io.getvalue()
        def Close(self):
            cam.cam.stop()
            cam.cam.close()
            self.isClosed = True
    
    print("Creating camera")
    cam = Camera()

    @app.route("/")
    def hello():
        global clientIsConnected
        #Turn back on the IR leds
        TurnOnLeds()
        clientIsConnected = True
        print("Client has connected")
        return open("index.html","r",encoding="utf-8").read()

    def gen():
        global timeOfLastSend, cam
        while True:
            if cam.isClosed:
                print("Reopening camera at",datetime.datetime.now().time())
                cam = Camera()
            frame = cam.GetFrame()
            timeOfLastSend = time.time()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/brightness', methods=['POST'])
    def receive_brightness():
        global brightness
        data = request.get_json()  # Parses JSON from request body
        brightness = data.get('brightness')
        print(f"Received brightness: {brightness}")
        return jsonify({"status": "success", "received": brightness})


    if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=False)
except:
    print(traceback.format_exc())
    try:
        cam.cam.stop()
        cam.cam.close()
    except: print("Failed to close camera")