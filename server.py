import traceback
try:
    # save this as app.py
    
    from flask import Flask, render_template, Response, request, jsonify
    import io
    import time
    from PIL import Image
    import RPi.GPIO as GPIO
    import time
    from threading import Thread
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    #import cv2
    brightness = 1.0
    oldBrightness = brightness
    ledPinList = [5,6]

    '''
    class ModulateLED():
        def __init__(self, pinNumber, brightness):
            self.pinNumber = pinNumber
            self.brightness = brightness
        def Start(self):
            GPIO.setup(6,GPIO.OUT)
            GPIO.output(6,GPIO.HIGH)
        def Update(self, newBrightness):
            pass
    '''
    def ModulateLED(pin):
        SCALE = 1#10**-1
        print("Modulating pin", pin)
        GPIO.output(pin,GPIO.HIGH)
        time.sleep((brightness)*SCALE)
        GPIO.output(pin,GPIO.LOW)
        time.sleep((1-brightness)*SCALE)
    
    threads = []
    for p in ledPinList:
        threads.append(Thread(target=ModulateLED, args=(p,)))

    def InitPins():
        print("Init Pins!")
        for p in ledPinList:
            GPIO.setup(p,GPIO.OUT)

    def StartLeds():
        print("Starting threads!")
        for t in threads:
            t.start()



    

    app = Flask(__name__)

    if False:
        class Camera():
            def __init__(self):
                self.imgList = [open(f"{i}.jpg", "rb").read() for i in range(1,3)]
                self.imgCounter = 0
            def GetFrame(self):
                print("Getting frame")
                img = self.imgList[self.imgCounter]
                self.imgCounter += 1
                if self.imgCounter >= len(self.imgList):
                    self.imgCounter = 0
                return img
    else:
        class Camera():
            def __init__(self): 
                from picamera2 import Picamera2
                self.cam = Picamera2()
                #config = self.cam.create_preview_configuration({"format": "MJPEG"})#M
                #self.cam.configure(config)
                #self.cam.configure(self.cam.create_still_configuration())
                #self.cam.start()
                self.cam.stop()
                self.cam.configure(
                    self.cam.create_still_configuration(main={"size": (1280,720)})
                )
                self.cam.set_controls({
                    "AfMode": 2,
                    "AfTrigger": 0  # Optional: triggers the autofocus cycle
                })
                self.cam.start()
                self.oldBrightness = brightness
            def GetFrame(self):
                # Capture as RGB array
                array = self.cam.capture_array()

                # Convert to JPEG bytes
                image = Image.fromarray(array)
                jpeg_io = io.BytesIO()
                image.save(jpeg_io, format="JPEG")
                #self.cam.stop()


                return jpeg_io.getvalue()


    @app.route("/")
    def hello():
        return open("index.html","r",encoding="utf-8").read()#render_template("index.html")

    def gen(camera):
        while True:
            #print("\n\n\n here \n\n\n")
            frame = camera.GetFrame()
            #print(type(frame))
            #input()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

 

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(Camera()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/brightness', methods=['POST'])
    def receive_brightness():
        global brightness
        data = request.get_json()  # Parses JSON from request body
        brightness = data.get('brightness')
        print(f"Received brightness: {brightness}")
        return jsonify({"status": "success", "received": brightness})


    if __name__ == '__main__':
        InitPins()
        StartLeds()
        app.run(host='0.0.0.0', debug=False)
except:
    print(traceback.format_exc())
    try:
        cam.cam.stop()
        cam.cam.close()
    except: print("Failed to close camera")