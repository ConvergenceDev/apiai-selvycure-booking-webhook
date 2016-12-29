# -*- coding: utf-8 -*-

from datetime import datetime
import time
import json
import os

from apscheduler.schedulers.background import BackgroundScheduler
import requests

FACEBOOK_SEND_URL = "https://graph.facebook.com/v2.6/me/messages"


class ActionProcessor(object):
    action = None
    request = None
    sender_id = None

    def __init__(self, action, request):
        super(ActionProcessor, self).__init__()
        self.action = action
        self.request = request
        self.__init_sender_id()

    def __init_sender_id(self):
        try:
            self.sender_id = self.request.get("originalRequest").get("data").get("sender").get("id")
        except AttributeError:
            print("can't extract sender id.")

    def process_request(self):
        pass


class BookingProcessor(ActionProcessor):
    def process_request(self):
        super(BookingProcessor, self).process_request()

        try:
            params = self.request.get("result").get("contexts")[0].get("parameters")
            booking_date = params.get("date")
            symptoms = params.get("cold-symptom")
            department = params.get("department")
            message = self.__get_message(booking_date)
            self.__reserve_message(message)
            self.__send_medical_certificate(str(symptoms))

        except AttributeError as e:
            print(e.message)

        return {}

    def __get_message(self, booking_date):
        return "{0} 병원 예약되어 있습니다.".format(booking_date)

    def __get_message_reservation_time(self):
        time = datetime.today()
        time = time.replace(second=time.second + 30)
        return time

    def __reserve_message(self, message):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.__send_message, 'date', run_date=self.__get_message_reservation_time(), args=message)
        scheduler.start()

    def __send_message(self, message):
        params = {
            "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": self.sender_id
            },
            "message": {
                "text": message
            }
        })

        r = requests.post(FACEBOOK_SEND_URL, params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)

    def __send_medical_certificate(self, symptom):
        params = {
            "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": self.sender_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "진단서",
                                "image_url": "http://mrg.bz/287967",
                                "subtitle": "증상: {0}".format(symptom),
                            }
                        ]
                    }
                }
            }
        })

        r = requests.post(FACEBOOK_SEND_URL, params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
        log(r.text)
