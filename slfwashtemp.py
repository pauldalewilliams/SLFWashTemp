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

twitter_send_tweet("Hello, world!")
gmail_send("pauldalewilliams@gmail.com", "Testing SLFWashTemp", "Hello, world!")
