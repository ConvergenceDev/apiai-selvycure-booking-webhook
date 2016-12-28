# -*- coding: utf-8 -*- 
# !/usr/bin/env python

from datetime import datetime
import json
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import request
from flask import make_response
import requests

# Flask app should start in global layout
APIAI_ACTION_NAME_BOOKING = "selvyCureBooking"
app = Flask(__name__)

FACEBOOK_SEND_URL = "https://graph.facebook.com/v2.6/me/messages"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = process_request(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'

    return r


def process_request(req):
    if req.get("result").get("action") != APIAI_ACTION_NAME_BOOKING:
        return {}

    try:
        sender_id = req.get("originalRequest").get("data").get("sender").get("id")
        booking_date = req.get("result").get("parameters").get("date")
        message = get_message(booking_date)
        reserve_message(sender_id, message)
    except AttributeError:
        print("can't extract sender id. ")
    return {}


def get_message(booking_date):
    return "{0} 병원 예약되어 있습니다.".format(booking_date)


def get_message_reservation_time():
    time = datetime.today()
    time = time.replace(second=time.second + 30)
    return time


def reserve_message(sender_id, message):
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_message, 'date', run_date=get_message_reservation_time(), args=(sender_id, message))
    scheduler.start()


def send_message(recipient_id, message):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message
        }
    })

    r = requests.post(FACEBOOK_SEND_URL, params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
