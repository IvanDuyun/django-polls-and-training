# (Task 8, part 2)
import requests
import time
from datetime import datetime as dt
import json
from django.core.signing import TimestampSigner


CNT_REQUESTS = 10
TIME_OUT = 1
SECRET_KEY = 'django-insecure-s58zd0^*xl)5w^sf750!=jc9)*d6m*0^-=lmcolfuo216-78@d'


def send_requests_for_training_cache(cnt, time_out=0):
    for i in range(cnt):
        resp = requests.get("http://127.0.0.1:8000/polls/")
        print('ответ на %s запрос: %s' % (i+1, resp))
        time.sleep(time_out)


def send_json_for_test_question_api(pk):
    sign = get_sign(pk)
    print(sign)
    param = {"pk": sign, "question_text": "how a uuuu", "pub_date": "2022-08-05 14:37:21", "author": "15"}
    json_param = json.dumps(param)
    url = "http://127.0.0.1:8000/polls/%s/private/" % pk
    resp = requests.post(url, data=json_param)
    print(resp.content)


def get_sign(text_sign):
    signer = TimestampSigner(SECRET_KEY)
    return signer.sign(text_sign)


send_json_for_test_question_api(3)
