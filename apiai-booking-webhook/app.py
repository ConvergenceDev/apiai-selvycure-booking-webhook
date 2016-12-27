#!/usr/bin/env python

from datetime import datetime
import urllib
import json
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import request
from flask import make_response
import requests

# Flask app should start in global layout
app = Flask(__name__)

FACEBOOK_SEND_URL = "https://graph.facebook.com/v2.6/me/messages"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "selvyCureBooking":
        return {}
        
    sender_id = req.get("originalRequest").get("data").get("sender").get("id")
    reserve_message(sender_id)
    return {}
#    
#    baseurl = "https://query.yahooapis.com/v1/public/yql?"
#    yql_query = makeYqlQuery(req)
#    if yql_query is None:
#        print("aa")
#        sender_id = "selvasai.convdev@gmail.com"
#        send_message(sender_id, "got it, thanks!")
#        return {}
#    print("bb")
#    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
#    result = urllib.urlopen(yql_url).read()
#    data = json.loads(result)
#    res = makeWebhookResult(data)
#    return res

def getMessageReservationTime(str_date):
    today = datetime.today()
    print(today)
    today.replace(minute=today.minute+1)
    print(today)
    return today
    
#    booking_time = datetime.strptime(str_date, '%M/%d')
#    
#    message_send_time = datetime.today()
#    message_send_time.month = booking_time.month
#    message_send_time.day = booking_time.day
#    
#    if today > message_send_time:
#        message_send_time.replace(year=message_send_time.year + 1)
#    message_send_time.replace(day=message_send_time.day-1)

def reserve_message(sender_id):
    sched = BackgroundScheduler()
    sched.add_job(send_message, 'date', run_date=getMessageReservationTime(''), args=(sender_id, "gg"))
    sched.start()
    
def send_message(recipient_id, message_text):
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
            "text": message_text
        }
    })
    
    print("id: ")
    print(recipient_id)
    
    print("text: ")
    print(message_text)
    
    r = requests.post(FACEBOOK_SEND_URL, params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    print(r.status_code)
    print(r.text)
    

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-selvycure-booking-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
