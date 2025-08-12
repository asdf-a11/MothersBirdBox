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
        from picamera2 import Picamera2
        self.cam = Picamera2()
        config = self.cam.create_preview_configuration({"format": "PNG"})#M
        self.cam.configure(config)

    def GetFrame(self):
        # Create an in-memory stream
        #my_stream = io.BytesIO()
        buffer = self.cam.capture_buffer()
        print("returning buffer,", type(buffer))
        return buffer#my_stream.getvalue()


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