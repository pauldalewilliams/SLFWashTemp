#!/usr/bin/python

import os
import glob
import time
import tweepy
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Insert VALUEs below based on this config:
#twitter_cfg = {
#    "consumer_key":"VALUE",
#    "consumer_secret":"VALUE",
#    "access_token":"VALUE",
#    "access_token_secret":"VALUE"
#    }
#
#gmail_address = "VALUE"
#gmail_password = "VALUE"
#gmail_recipient = "VALUE"
#gmail_SMTP_server = "smtp.gmail.com"
#gmail_SMTP_port = 587



# End VALUEs section

def twitter_get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)

def twitter_send_tweet(tweet):
    api = twitter_get_api(twitter_cfg)
    status = api.update_status(status=tweet)
    return

def gmail_send(subject, body):
    msg = MIMEMultipart()
    msg['From'] = gmail_address
    msg['To'] = gmail_recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP(gmail_SMTP_server, gmail_SMTP_port)
    server.ehlo()
    server.starttls()
    server.login(gmail_address, gmail_password)
    text = msg.as_string()
    server.sendmail(gmail_address, gmail_recipient, text)
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
        temp_c = round(temp_c, 1)
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        temp_f = round(temp_f, 0)
        return int(temp_f)

def read_temp_oneminavg():
    readings = 0.0
    total = 0.0
    for i in range(0, 10):
        current_temp = read_temp()
        if current_temp:
            readings += 1
            total += current_temp
            current_time = time.asctime(time.localtime(time.time()))
            status = current_time + " - Current temp = " + str(current_temp) + "F"
            print (status)
        time.sleep(6)
    avg_temp = total / readings
    avg_temp = round(avg_temp, 0)
    return int(avg_temp)

def read_temp_thirtyminstats():
    readings = 0.0
    min_temp = 300
    max_temp = 0
    total = 0.0
    for i in range(0, 300):
        current_temp = read_temp()
        if current_temp:
            readings += 1
            total += current_temp
            if current_temp < min_temp:
                min_temp = current_temp
                print("New minimum temp")
            if current_temp > max_temp:
                max_temp = current_temp
                print("New maximum temp")
            current_time = time.asctime(time.localtime(time.time()))
            status = current_time + " - Current temp = " + str(current_temp) + "F"
            print(status)
        time.sleep(6)
    avg_temp = total / readings
    avg_temp = round(avg_temp, 0)
    if avg_temp == 0:
        twitter_send_tweet("No valid temperature readings for the past 30 minutes.  Please check me!")
        gmail_send("No Temperature Readings", "I haven't had a valid temperature reading for the past 30 minutes.  Better check on me!")
        return None, None, None
    else:
        return int(min_temp), int(max_temp), int(avg_temp)

def monitor_temperature():
    last_peak_time = int(time.time())
    alert_sent = 0
    twitter_send_tweet("Starting to monitor the temperature now.  I'll post stats in 30 minutes.")
    while True:
        current_min_temp, current_max_temp, current_avg_temp = read_temp_thirtyminstats()
        if current_avg_temp is None:
            while read_temp_oneminavg() == 0:
                time.sleep(10)
            twitter_send_tweet("Looks like I'm getting temperature data now!  I'll post stats in 30 minutes.")
            continue
        current_time = time.asctime(time.localtime(time.time()))
        current_epoch_time = int(time.time())
        tweet = "Min = " + str(current_min_temp) + "F | Max = " + str(current_max_temp) + "F | Avg = " + str(current_avg_temp) + "F as of " + current_time + " during the past 30 minutes"
        twitter_send_tweet(tweet)
        if current_max_temp >= 115:
            last_peak_time = current_epoch_time
            twitter_send_tweet("Wash cycle ran in the last 30 minutes.  Ready for the next milking!")
            if alert_sent == 1:
                gmail_send("Milk Pipe Has Been Washed!", 
                           "It looks like the milk pipe has been washed after missing the last cycle, or my temperature sensor is finally working.")
            alert_sent = 0
        elif current_epoch_time - last_peak_time > 43200:
            if alert_sent == 0:
                gmail_send("May Need to Wash Milk Pipe",
                           "It's been more than 12 hours since the milk pipe has been washed.  Someone may have forgotten to run the wash cycle.  Better double check!")
                alert_sent = 1

# Setup temperature sensor

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

monitor_temperature()
