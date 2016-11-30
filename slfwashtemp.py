#!/usr/bin/python

import os
import glob
import time
import tweepy
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Change VALUEs below

twitter_cfg = {
    "consumer_key":"VALUE",
    "consumer_secret":"VALUE",
    "access_token":"VALUE",
    "access_token_secret":"VALUE"
    }

gmail_address = "VALUE"
gmail_password = "VALUE"
gmail_SMTP_server = "smtp.gmail.com"
gmail_SMTP_port = 587

# End VALUE change section

def twitter_get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)

def twitter_send_tweet(tweet):
    api = twitter_get_api(twitter_cfg)
    status = api.update_status(status=tweet)
    return

def gmail_send(toaddress, subject, body):
    msg = MIMEMultipart()
    msg['From'] = gmail_address
    msg['To'] = toaddress
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP(gmail_SMTP_server, gmail_SMTP_port)
    server.ehlo()
    server.starttls()
    server.login(gmail_address, gmail_password)
    text = msg.as_string()
    server.sendmail(gmail_address, toaddress, text)
    server.quit()
    return

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f


# Setup temperature sensor

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

while True:
    print(read_temp())	
    time.sleep(1)
