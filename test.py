from PIL import Image


with open(R"C:\Users\willi\Downloads\test.jpg","rb") as f:
    b = f.read()

img = Image.frombytes(b)
img.show()
