import io
import os
import picamera
import threading
import subprocess
import time
import datetime
import pyttsx
import imaplib
import pywapi
import unicodedata
import RPi.GPIO as GPIO
from bottle import route, run, template, request
#from pydub import AudioSegment
#import cherrypy.wsgiserver
#from flask import Flask
from PIL import Image

# Motion detection settings:
# Threshold (how much a pixel has to change by to be marked as "changed")
# Sensitivity (how many changed pixels before action is taken)
threshold = 20
sensitivity = 20
camera = picamera.PiCamera()
GPIO.setmode(GPIO.BCM)
CAMLED = 5
GPIO.setup(CAMLED, GPIO.OUT, initial=False)
stylestring = "<style>html * {font-size:72}</style>"
#app = Flask(__name__)
#d = cherrypy.wsgiserver.WSGIPathInfoDispatcher({'/':app})
#server = cherrypi.wsgiserver.CherryPyWSGIServer(('0.0.0.0',80),d)
@route("/")
def home():
    return stylestring + template("<h1>Music Server</h1><p>{{hour}}:{{minute}}</p><p><a href='/alarm'>Alarm</a></p><p><a href='/alarm2'>Reminder</a></p><p><a href='/music'>Music</a></p><p><a href='/upload'>Upload</a></p><p><a href='/delete'>Delete</a></p><p><a href='/restart'>Reboot</a></p><p><a href='/power'>Shutdown</a></p>", hour=datetime.datetime.now().hour,minute=datetime.datetime.now().minute)
@route("/music")
def music():
    global musicnum
    if occupied == True:
        return stylestring + template("<h1>Music</h1><p>Currently playing {{file}}</p><p><a href='/stop'>Stop</a></p><p><a href='/'>Home</a></p>", file=sorted(os.listdir("music/"))[musicnum])
    if len(os.listdir("music/")) == 0:
        return stylestring + "<h1>Music</h1><p>Nothing to play. Please upload some music.</p><a href='/'>Home</a>"
    if musicnum+1 >= len(os.listdir("music/")):
        return stylestring + template("<h1>Music</h1><p>Currently not playing. Next up {{file}}</p><p><a href='/play'>Play</a></p><p><a href='/'>Home</a></p>", file=sorted(os.listdir("music/"))[0])
    return stylestring + template("<h1>Music</h1><p>Currently not playing. Next up {{file}}</p><p><a href='/play'>Play</a></p><p><a href='/'>Home</a></p>", file=sorted(os.listdir("music/"))[musicnum+1])
@route("/alarm")
def alarm():
    global hour, minute, alarmset
    return stylestring + template("<h1>Alarm</h1><p>Alarm status: {{alarmset}}</p><p>Alarm set for {{hour}}:{{minute}}</p><a href='/on'>Turn alarm on</a><br /><a href='/off'>Turn alarm off</a><br /><a href='/set'>Set alarm time</a>", alarmset=alarmset, hour=hour, minute=minute)
@route("/on")
def on():
    global alarmset
    alarmset = True
    return stylestring + "<p>Alarm on. <a href='/'>Home</a></p>"
@route("/off")
def off():
    global alarmset
    alarmset = False
    return stylestring + "<p>Alarm off. <a href='/'>Home</a></p>"
@route("/set")
def set():
    return stylestring + "<form action='/time' method='post'>Hour:<input type='text' name='hour' />Minute:<input type='text' name='minute' /><input type='submit' value='Set' /></form>"
@route("/time", method='POST')
def setalarm():
    global hour, minute
    hour = int(request.forms.get('hour'))
    minute = int(request.forms.get('minute'))
    return stylestring + "<p>Alarm set. <a href='/'>Home</a></p>"
@route("/play")
def play():
    global occupied
    music()
    occupied=True
    return stylestring + "<p>Music started</p><p><a href='/'>Home</a></p>"
@route("/stop")
def stop():
    global occupied,musicprocess
    occupied = False
    musicprocess.stdin.write("q")
    return stylestring + "<p>Music stopped</p><p><a href='/'>Home</a></p>"
@route("/upload")
def upload():
    return stylestring + "<form action='/save' method='post' enctype='multipart/form-data'><input type='file' name='upload[]' multiple /><input type='submit' value='Upload' /></form>"
@route("/save",method='POST')
def save():
    upload = request.files.getlist('upload[]')
    for u in upload:
        u.save("music/")
    return stylestring + "<p>Upload successful. <a href='/'>Home</a></p>"
@route("/delete")
def delete():
    global musicnum
    os.system("rm -rfv music/")
    os.system("mkdir music")
    musicnum = 0
    return stylestring + "<p>Cleared music folder. <a href='/'>Home</a></p>"
@route("/restart")
def restart():
    os.system("sudo reboot")
    return stylestring + "<p>Rebooting... please wait</p>"
@route("/power")
def turnoff():
    os.system("sudo shutdown -h now")
    return stylestring + "<p>Shutting down...</p>"
@route("/alarm2")
def alarm2():
    global hour2, minute2, reminder, remindertext
    return stylestring + template("<h1>Reminder</h1><p>Reminder status: {{reminder}}</p><p>Reminder set for {{hour2}}:{{minute2}}</p><p>Reminder text is {{remindertext}}</p><a href='/set2'>Set reminder time</a><br /><a href='/set3'>Set reminder text</a><br /><a href='/'>Back to home</a>", reminder=reminder,remindertext=remindertext, hour2=hour2, minute2=minute2)
@route("/on2")
def on2():
    global reminder
    reminder = True
    return stylestring + "<p>Reminder on. <a href='/'>Home</a></p>"
@route("/off2")
def off2():
    global reminder
    reminder = False
    return stylestring + "<p>Reminder off. <a href='/'>Home</a></p>"
@route("/set2")
def set2():
    return stylestring + "<form action='/time2' method='post'>Hour:<input type='text' name='hour' />Minute:<input type='text' name='minute' /><input type='submit' value='Set' /></form>"
@route("/time2", method='POST')
def setalarm2():
    global hour2, minute2
    hour2 = int(request.forms.get('hour'))
    minute2 = int(request.forms.get('minute'))
    return stylestring + "<p>Reminder set. <a href='/'>Home</a></p>"
@route("/set3")
def settext3():
    return stylestring + "<form action='/text' method='post'>Text:<input type='text' name='newtext' /><input type='submit' value='Set' /></form>"
@route("/text", method='POST')
def textset():
    global remindertext, reminder
    reminder = True
    remindertext = request.forms.get('newtext')
    return stylestring + "<p>Reminder text set. Reminder turned ON. <a href='/'>Home</a></p>"
# Capture a small test image (for motion detection)
def captureTestImage():
    camera.resolution = (50, 25)
    stream = io.BytesIO()
    camera.capture(stream, format='bmp')
    stream.seek(0)
    im = Image.open(stream)
    buffer = im.load()
    stream.close()
    return buffer

# Get first image
#global image1
#global buffer1

#image1 = captureTestImage()
buffer1 = captureTestImage()
def chatthread():
    pass

def alarmthread():
    global hour2, minute2, reminder, remindertext
    while True:
        if datetime.datetime.now().hour == hour2 and datetime.datetime.now().minute == minute2 and reminder == True:
            engine = pyttsx.init()
            engine.say(remindertext)
            engine.runAndWait()
            reminder = False
def motionthread():
    global buffer1, occupied, hour, musicprocess, minute, alarmset
    while True:
        # Get comparison image
        buffer2 = captureTestImage()

        # Count changed pixels
        changedPixels = 0
        for x in xrange(0, 50):
            for y in xrange(0, 25):
                # Just check green channel as it's the highest quality channel
                pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
                if pixdiff > threshold:
                    changedPixels += 1
                
        # Take action if pixels changed
        if changedPixels > sensitivity:
            action()
        if datetime.datetime.now().hour == hour and datetime.datetime.now().minute == minute and alarmset == True:
            forecasttext = unicodedata.normalize('NFKD', pywapi.get_weather_from_yahoo('84003', '')['forecasts'][0]['text']).encode('ascii','ignore')
            engine = pyttsx.init()
            engine.say("The weather today is "+forecasttext)
            engine.runAndWait()
            music()
            occupied = True
        # Swap comparison buffers
        #image1 = image2
        buffer1 = buffer2
        if occupied == True:
            quit = False    
        else:
            quit = True
        while not quit:
            musicprocess.wait()
            buffer2 = captureTestImage()
            buffer1 = buffer2
            occupied = False
            quit = True
def action():
    global occupied
    if datetime.datetime.now().hour < 21 and datetime.datetime.now().hour >= 6:
        GPIO.output(CAMLED,True)
        imap = imaplib.IMAP4_SSL("imap.gmail.com",'993')
        imap.login("youremail@gmail.com","password")
        imap.select()
        imap.check()
        unread = len(imap.search(None,'UnSeen')[1][0].split())
        imap.logout()
        if unread > 0:
            engine = pyttsx.init()
            engine.say("You have "+str(unread)+" new emails.")
            engine.runAndWait()
        GPIO.output(CAMLED,False)
        music()
        occupied = True
        #occupiedtimer.cancel()
        #occupiedtimer = threading.Timer(10,leave)
        #occupiedtimer.start()
def leave():
    global occupied
    #if pygame.mixer.get_init() == True:
    #    pygame.mixer.music.stop()
    #occupied = False
def music():
    global musicnum,musicprocess
    if len(os.listdir("music/")) == 0:
        return
    musicnum += 1
    if musicnum >= len(os.listdir("music/")):
        musicnum = 0
    musicprocess = subprocess.Popen(["mplayer", "music/"+sorted(os.listdir("music/"))[musicnum]], stdin=subprocess.PIPE)
# Begin start of server
occupied = False
musicprocess = None
hour = 0
minute = 0
hour2 = 0
minute2 = 0
reminder = False
remindertext = ""
alarmset = False
musicnum = len(os.listdir("music/")) -1
#occupiedtimer = threading.Timer(10,leave)
#occupiedtimer.start()
#motionthread()
motion = threading.Thread(target=motionthread)
motion.daemon = True
motion.start()
alarma = threading.Thread(target=alarmthread)
alarma.daemon = True
alarma.start()
#if __name__ == "__main__":
#if __name__ == "__main__":
#    try:
#        server.start()
#    except KeyboardInterrupt:
#        server.stop()
run(host='0.0.0.0', port=8080, debug=True)
while True:
    pass
