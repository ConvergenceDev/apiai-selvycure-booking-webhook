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
            symptoms = ",".join(symptom.encode('utf-8') for symptom in params.get("cold-symptom"))
            department = params.get("department").encode('utf-8')
            message = self.__get_message(booking_date)
            # self.__reserve_message(message)
            self.__send_medical_certificate(symptoms, booking_date, department)
            self.__send_medical_certificate2(symptoms, booking_date, department)

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
                                "image_url": "https://cdn.pixabay.com/photo/2013/07/13/13/34/diagnostics-161140_960_720.png",
                                "subtitle": "환자 증상: {0}, 진료 예약 날짜: {1}, 진료과: {2}".format(symptom, booking_date,
                                                                                         department),
                            },
                            {
                                "title": "감기 원인",
                                "subtitle": "200여개 이상의 서로 다른 종류의 바이러스가 감기를 일으킨다. 감기 바이러스는 사람의 코나 목을 통해 들어와 감염을 일으킨다.",
                            },
                            {
                                "title": "감기 관련 증상",
                                "subtitle": "기침, 인두통 및 인후통, 비루, 비폐색, 재채기, 근육통, 발열",
                            },
                            {
                                "title": "진료과",
                                "subtitle": "가정의학과, 감염내과, 호흡기내과, 소아청소년과, 이비인후과",
                            },
                            {
                                "title": "예방방법",
                                "subtitle": "감기 바이러스 접촉 기회를 차단해야 한다. 손을 자주 씻어 감기 바이러스를 없애고 손으로 눈이나 코, 입을 비비지 않도록 한다.",
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
                        "template_type": "list",
                        "elements": [
                            {
                                "title": "진단서",
                                "image_url": "https://cdn.pixabay.com/photo/2013/07/13/13/34/diagnostics-161140_960_720.png",
                                "subtitle": "환자 증상: {0}, 진료 예약 날짜: {1}, 진료과: {2}".format(symptom, booking_date,
                                                                                         department),
                            },
                            {
                                "title": "감기 원인",
                                "subtitle": "200여개 이상의 서로 다른 종류의 바이러스가 감기를 일으킨다. 감기 바이러스는 사람의 코나 목을 통해 들어와 감염을 일으킨다.",
                            },
                            {
                                "title": "감기 관련 증상",
                                "subtitle": "기침, 인두통 및 인후통, 비루, 비폐색, 재채기, 근육통, 발열",
                            },
                            {
                                "title": "진료과",
                                "subtitle": "가정의학과, 감염내과, 호흡기내과, 소아청소년과, 이비인후과",
                            },
                            {
                                "title": "예방방법",
                                "subtitle": "감기 바이러스 접촉 기회를 차단해야 한다. 손을 자주 씻어 감기 바이러스를 없애고 손으로 눈이나 코, 입을 비비지 않도록 한다.",
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
