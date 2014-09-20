from datetime import datetime
from flask import Flask, render_template, request
from time import sleep
import glob
import os, shutil
from local_settings import DOWNLOAD_DIR, CURRENT_PATH, SNAPSHOT_DIR, MAX_FILES, LIVE
if LIVE:
    import picamera
    import RPi.GPIO as GPIO

DEFAULT_EXPOSURE = 0.1

app = Flask(__name__)

def getImageList():
    return map(os.path.basename, glob.glob(SNAPSHOT_DIR + '*.jpg'))

def snap(filename):
    camLock = True
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        # Camera warm-up time
        sleep(2)
        camera.capture(filename)
    camLock = False
    return True

@app.route("/",methods=['GET', 'POST'])
def home():
    print SNAPSHOT_DIR
    templateData = {
      'images' : getImageList(),
    }
    camLock = False
    now = datetime.now()
    images = getImageList()
    if request.method == 'POST':
        if camLock:
            return render_template('home.html', **templateData)
        filename = os.path.join(SNAPSHOT_DIR,now.strftime("image-%Y-%m-%dT%H:%m:%s.jpg"))
        newfile = os.path.join(SNAPSHOT_DIR,"latest.jpg")
        snap(filename)
        shutil.copy(filename,newfile)
        templateData['filename']= "latest.jpg"
    else:
        if len(images)>0:
            templateData['filename'] = images[0]
        else:
            templateData['filename']=None
    return render_template('home.html', **templateData)



if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080, debug=True)
