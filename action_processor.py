# -*- coding: utf-8 -*-

from datetime import datetime
import json

from apscheduler.schedulers.background import BackgroundScheduler
import requests

FACEBOOK_SEND_URL = "https://graph.facebook.com/v2.6/me/messages"


class ActionProcessor(object):
    action = None
    request = None
    sender_id = None
    page_access_token = None

    def __init__(self, action, request, token):
        super(ActionProcessor, self).__init__()
        self.action = action
        self.request = request
        self.page_access_token = token
        self.__init_sender_id()

    def __init_sender_id(self):
        try:
            self.sender_id = self.request.get("originalRequest").get("data").get("sender").get("id")
        except AttributeError:
            print("can't extract sender id.")

    def process_request(self):
        pass


class BookingProcessor(ActionProcessor):
    def __init__(self, action, request, token):
        super(BookingProcessor, self).__init__(action, request, token)

    def process_request(self):
        super(BookingProcessor, self).process_request()

        try:
            params = self.request.get("result").get("contexts")[0].get("parameters")
            booking_date = params.get("date")
            symptoms = params.get("cold-symptom")
            department = params.get("department")
            message = self.__get_message(booking_date)
            # self.__reserve_message(message)
            self.__send_medical_certificate(str(symptoms), booking_date, department)
            self.__send_medical_certificate2(str(symptoms), booking_date, department)

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
        print("message: {0}".format(message))
        scheduler.add_job(self.send_message, 'date', run_date=self.__get_message_reservation_time(), args=message)
        scheduler.start()

    def send_message(self, message):
        print("token: {0}".format(self.page_access_token))
        print("sender_id: {0}".format(self.sender_id))

        params = {
            "access_token": self.page_access_token
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

    def __send_medical_certificate(self, symptom, booking_date, department):
        params = {
            "access_token": self.page_access_token
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
                                "subtitle": "환자 증상: {0}\n진료 예약 날짜: {1}".format(symptom, booking_date),
                            },
                            {
                                "title": "원인",
                                "subtitle": "200여개 이상의 서로 다른 종류의 바이러스가 감기를 일으킨다. 감기 바이러스는 사람의 코나 목을 통해 들어와 감염을 일으킨다.",
                            }
                        ]
                    }
                }
            }
        })
        headers = {
            "Content-Type": "application/json"
        }

        r = requests.post(FACEBOOK_SEND_URL, params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)


    def __send_medical_certificate2(self, symptom, booking_date, department):
        params = {
            "access_token": self.page_access_token
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
                                "subtitle": "환자 증상: {0}\n진료 예약 날짜: {1}".format(symptom, booking_date),
                            },
                            {
                                "title": "원인",
                                "subtitle": "200여개 이상의 서로 다른 종류의 바이러스가 감기를 일으킨다. 감기 바이러스는 사람의 코나 목을 통해 들어와 감염을 일으킨다.",
                            }
                        ]
                    }
                }
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "receipt",
                        "recipient_name": "진단서",
                        "order_number": "1",
                        "currency": "USD",
                        "payment_method": "Visa 2345",
                        "elements": [
                            {
                                "title": "진단서",
                                "subtitle": "환자 증상: {0}<br>진료 예약 날짜: {1}<br>진료과: {2}".format(symptom, booking_date, department),
                                "price": 50,
                            },
                            {
                                "title": "감기의 원인",
                                "subtitle": "200여개 이상의 서로 다른 종류의 바이러스가 감기를 일으킨다. 감기 바이러스는 사람의 코나 목을 통해 들어와 감염을 일으킨다.",
                                "price": 50,
                            }
                        ],
                        "summary": {
                            "subtotal": 75.00,
                            "shipping_cost": 4.95,
                            "total_tax": 6.19,
                            "total_cost": 56.14
                        }
                    }
                }
            }
        })
        headers = {
            "Content-Type": "application/json"
        }

        r = requests.post(FACEBOOK_SEND_URL, params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)