from flask import Flask, request, redirect, url_for, render_template
import os
import json
import glob
from uuid import uuid4
import cv2   
import numpy as np

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "uploadr/static/uploads/{}".format(upload_key)
    try:
        os.mkdir(target)
    except:
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)

    print("=== Form Data ===")
    for key, value in list(form.items()):
        print(key, "=>", value)

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("upload_complete", uuid=upload_key))


@app.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "uploadr/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = {}
    print("1st checkpoint   ")
    for file in glob.glob("{}/*.*".format(root)):
        print(file)
        fname = file.split(os.sep)[-1]
        files[fname]=checkBlueColor(file)
        #files.append(fname)


    """ files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname) """

    return render_template("files.html",
        uuid=uuid,
        files=files,
    )


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))


def checkBlueColor(imgPath):
    frame = cv2.imread(imgPath)
    
    img = frame

    #convert BGR to HSV
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    #define Range of colors
    blue_lower=np.array([99,115,150],np.uint8)
    blue_upper=np.array([110,255,255],np.uint8)


    blue=cv2.inRange(hsv,blue_lower,blue_upper)
    kernal = np.ones((5 ,5), "uint8")
    #print("kernal done")

    #find blue contours
    blue=cv2.dilate(blue,kernal)
    res1=cv2.bitwise_and(img, img, mask = blue)
    (_,contours,hierarchy)=cv2.findContours(blue,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    count=0
    ImgBlueStat="no"
    #print file path for no blue detect. 
    if(contours==[]):
        print(imgPath)
        return "NO"
    else:
        for pic, contour in enumerate(contours):
            
            area = cv2.contourArea(contour)
            
            if(area>300):
                
                if(count==0):

                    #print fpath and yes only once.
                    print(imgPath, "yes")
                    count=count+1
                    return "yes"
                
                x,y,w,h = cv2.boundingRect(contour)	
                img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                cv2.putText(img,"Blue color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150,0,0))



