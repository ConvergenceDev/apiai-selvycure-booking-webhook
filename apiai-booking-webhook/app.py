#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


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
    send_message(sender_id, "got it, thanks!")
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
    
def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    print("token: ")
    print(os.environ["PAGE_ACCESS_TOKEN"])
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    print(params)
    headers = {
        "Content-Type": "application/json"
    }
    print(headers)
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    print(data)
    print("send id: ")
    print(recipient_id)
    
    print("access_token: ")
    print(os.environ["PAGE_ACCESS_TOKEN"])
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
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
