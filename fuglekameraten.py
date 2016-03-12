# -*- coding: latin-1 -*-

import RPi.GPIO as GPIO
import time
import datetime
import smtplib # Import smtplib for the actual sending function
from email.mime.text import MIMEText # Import the email modules we'll need
from twython import Twython, TwythonError # Twitter bibliotek
import urllib2 # used to verify internet connection

# Antall sekunder uten bevegelse før vi poster ny tweet
twitter_delay = 3600 # 1 time

# Funksjoner
def internet_on():
    try:
        response=urllib2.urlopen('http://216.58.209.99', timeout=5)
        return True
    except urllib2.URLError as err: pass
    return False

def discharge():
    GPIO.setup(a_pin, GPIO.IN)
    GPIO.setup(b_pin, GPIO.OUT)
    GPIO.output(b_pin, False)
    time.sleep(0.005)

def charge_time():
    GPIO.setup(b_pin, GPIO.IN)
    GPIO.setup(a_pin, GPIO.OUT)
    count = 0
    GPIO.output(a_pin, True)
    while not GPIO.input(b_pin):
        count = count + 1
    return count

def analog_read():
    discharge()
    return charge_time()

def send_email():
    s = smtplib.SMTP('smtp.altibox.no')
    s.sendmail(fra, til, msg.as_string())
    s.quit()

def post_tweet():
    try:
        twitter.update_status(status='Fuglekameraten har detektert bevegelse i fuglekassen! Klikk her: http://www.forskerklubben.no/fuglekamera/ (' + time.strftime("%b %d %Y %H:%M:%S", time.gmtime(time.time())) + ')')
    except TwythonError as e:
        print e

print("Startup")
while not internet_on():
	print("No Internet connection!")
	time.sleep(1)
print("We have Internet connection. Continuing ...")

# twitter setup
f_app_key = open("/data/forskerklubben/fuglekameraten/app_key.txt")
APP_KEY = f_app_key.read()
f_app_key.close()
f_app_secret = open("/data/forskerklubben/fuglekameraten/app_secret.txt")
APP_SECRET = f_app_secret.read()
f_app_secret.close()
f_oauth_token = open("/data/forskerklubben/fuglekameraten/oauth_token.txt")
OAUTH_TOKEN = f_oauth_token.read()
f_oauth_token.close()
f_oauth_token_secret = open("/data/forskerklubben/fuglekameraten/oauth_token_secret.txt")
OAUTH_TOKEN_SECRET = f_oauth_token_secret.read()
f_oauth_token_secret.close()
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

print("Twitter OK")
# epost setup
f_fra = open("/data/forskerklubben/fuglekameraten/fra.txt")
fra = f_fra.read()
f_fra.close()

til = []
tilmsg = ""
with open("/data/forskerklubben/fuglekameraten/to.txt") as f_to:
    til = f_to.readlines()
msg = MIMEText("Fuglekameraten har detektert bevegelse i fuglekassen! Klikk her: http://www.forskerklubben.no/fuglekamera/")
msg['Subject'] = 'Bevegelse i fuglekassen!'
msg['From'] = fra
for to in til:
    tilmsg += to + ","
msg['To'] = tilmsg

print("Email OK")
# IO setup
led_pin = 3
a_pin = 5
b_pin = 7
pir_pin = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(pir_pin, GPIO.IN, GPIO.PUD_DOWN)

# initialisering av variabler
previous_state = False
current_state = False
timestamp = time.time()

print("Starting program")
while True:
    # Les lys sensor
    value = analog_read()
    
    # Skru på lys dersom lyssensoren gir høyere verdi enn 100
    if (value > 100):
        GPIO.output(led_pin, True)
    else:
        GPIO.output(led_pin, False)

    # Bevegelse sensor
    previous_state = current_state
    current_state = GPIO.input(pir_pin)
    if current_state != previous_state:
        print(GPIO.input(pir_pin))
        if current_state == False:
            timestamp = time.time()
        else:
            motion = time.time()
            delta = motion - timestamp
            if (delta > twitter_delay):
                #print("Tweet")
                send_email()
                post_tweet()

    time.sleep(1)
