#!/usr/bin/env python

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

def getMessageReservationTime(str_date):
    today = datetime.today()
    today.replace(second=today.second+10)
    print(today)
    return today

def reserve_message(sender_id):
    sched = BackgroundScheduler()
    sched.add_job(send_message, 'date', run_date=getMessageReservationTime(''), args=(sender_id, "gg"))
    sched.start()
    
def send_message(recipient_id, message_text):
    print(recipient_id)
    print(message_text)
if __name__ == '__main__':
#    port = int(os.getenv('PORT', 5000))
#
#    print "Starting app on port %d" % port
#
#    app.run(debug=False, port=port, host='0.0.0.0')
    reserve_message("11")