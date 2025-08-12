# save this as app.py
from flask import Flask, render_template, Response

app = Flask(__name__)

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