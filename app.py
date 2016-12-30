# -*- coding: utf-8 -*- 
# !/usr/bin/env python

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
from action_processor import BookingProcessor

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
    response = None

    try:
        action = req.get("result").get("action")

        if action == APIAI_ACTION_NAME_BOOKING:
            response = BookingProcessor(action, req)
    except AttributeError:
        print("can't extract action.")
        return {}

    if response is not None:
        return response.process_request()

    return {}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
