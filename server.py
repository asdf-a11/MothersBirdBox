# save this as app.py
try:
    from flask import Flask, render_template, Response
except Exception:
    import os
    os.system("pip install flask")
    from flask import Flask, render_template, Response
import io
import time


app = Flask(__name__)

'''
class Camera():
    def __init__(self):
        self.imgList = [open(f"{i}.jpg", "rb").read() for i in range(1,3)]
        self.imgCounter = 0
    def GetFrame(self):
      img = self.imgList[self.imgCounter]
      self.imgCounter += 1
      if self.imgCounter >= len(self.imgList):
          self.imgCounter = 0
      return img
'''
class Camera():
    def __init__(self): 
        import picamera2 as picamera
        self.cam = picamera.PiCamera()
    def GetFrame(self):
        #from picamzero import Camera
        #cam = Camera()
        #import io        # Create an in-memory stream
        stream = io.BytesIO()
        self.cam.resolution = (1024, 768)
        self.cam.start_preview()        
        # Optional: warm-up time        
        #time.sleep(0.01)        
        # Capture to the stream
        self.cam.capture(stream, format='jpeg')
        # Get the byte buffer
        image_bytes = stream.getvalue()
        # Now `image_bytes` contains the JPEG image data
        return image_bytes


@app.route("/")
def hello():
    return open("index.html","r",encoding="utf-8").read()#render_template("index.html")

def gen(camera):
    while True:
        frame = camera.GetFrame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
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