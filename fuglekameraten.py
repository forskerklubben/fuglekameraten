# -*- coding: latin-1 -*-

import RPi.GPIO as GPIO
import time
import datetime
import smtplib # Import smtplib for the actual sending function
from email.mime.text import MIMEText # Import the email modules we'll need
from twython import Twython, TwythonError # Twitter bibliotek

# Antall sekunder uten bevegelse f�r vi poster ny tweet
twitter_delay = 10

# twitter setup
f_app_key = open("./app_key.txt")
APP_KEY = f_app_key.read()
f_app_key.close()
f_app_secret = open("./app_secret.txt")
APP_SECRET = f_app_secret.read()
f_app_secret.close()
f_oauth_token = open("./oauth_token.txt")
OAUTH_TOKEN = f_oauth_token.read()
f_oauth_token.close()
f_oauth_token_secret = open("./oauth_token_secret.txt")
OAUTH_TOKEN_SECRET = f_oauth_token_secret.read()
f_oauth_token_secret.close()
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# epost setup
f_fra = open("./fra.txt")
fra = f_fra.read()
f_fra.close()

til = []
with open("./to.txt") as f_to:
    til = f_to.readlines()
msg = MIMEText("Fuglekameraten har detektert bevegelse i fuglekassen! Klikk her: http://www.forskerklubben.no/fuglekamera/")
msg['Subject'] = 'Bevegelse i fuglekassen!'
msg['From'] = fra
msg['To'] = til

# IO setup
led_pin = 3
a_pin = 5
b_pin = 7
pir_pin = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(pir_pin, GPIO.IN, GPIO.PUD_DOWN)

# initialisering av variabler
previous_state = False
current_state = False
timestamp = time.time()

# Funksjoner
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
        twitter.update_status(status='Fuglekameraten har detektert bevegelse i fuglekassen! Klikk her: http://www.forskerklubben.no/fuglekamera/')
    except TwythonError as e:
        print e

while True:

    # Les lys sensor
    value = analog_read()
    
    # Skru p� lys dersom lyssensoren gir h�yere verdi enn 100
    if (value > 100):
        GPIO.output(led_pin, True)
    else:
        GPIO.output(led_pin, False)

    # Bevegelse sensor
    previous_state = current_state
    current_state = GPIO.input(pir_pin)
    if current_state != previous_state:
        if current_state == False:
            timestamp = time.time()
        else:
            motion = time.time()
            delta = motion - timestamp
            if (delta > twitter_delay):
                send_email()
                post_tweet()

    time.sleep(1)
