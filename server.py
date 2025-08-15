import traceback
try:
    # save this as app.py
    
    from flask import Flask, render_template, Response, request, jsonify
    import io
    import time
    from PIL import Image
    #import cv2
    brightness = 1.0

    def SetLED():
        import RPi.GPIO as GPIO
        import time
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(6,GPIO.OUT)
        # set GPIO14 pin to HIGH
        GPIO.output(6,GPIO.HIGH)
        print(brightness)

    

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
                SetLED()
                self.oldBrightness = brightness
            def GetFrame(self):
                # Capture as RGB array
                array = self.cam.capture_array()

                # Convert to JPEG bytes
                image = Image.fromarray(array)
                jpeg_io = io.BytesIO()
                image.save(jpeg_io, format="JPEG")
                #self.cam.stop()

                print(self.oldBrightness, brightness)
                if self.oldBrightness != brightness:
                    self.oldBrightness = brightness
                    print("update brightness")
                    #UpdateBrightness()

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
        data = request.get_json()  # Parses JSON from request body
        brightness = data.get('brightness')
        print(f"Received brightness: {brightness}")
        return jsonify({"status": "success", "received": brightness})


    if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=False)
    '''
    from flask import Flask, render_template, Response

    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    def gen(camera):
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    @app.route('/video_feed')
    def video_feed():
        return Response(gen(Camera()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=True)
    '''
except:
    print(traceback.format_exc())
    try:
        cam.cam.stop()
        cam.cam.close()
    except: print("Failed to close camera")