# (Task 8, part 2)
import requests
import time


CNT_REQUESTS = 10
TIME_OUT = 1


def send_requests_for_training_cache(cnt, time_out=0):
    for i in range(cnt):
        res = requests.get("http://127.0.0.1:8000/polls/")
        print('ответ на %s запрос: %s' % (i+1, res))
        time.sleep(time_out)


def send_specific_requests_for_training_cache():
    res = requests.get("http://127.0.0.1:8000/polls/")
    print('ответ на %s запрос: %s' % (1, res))
    time.sleep(3)
    res = requests.get("http://127.0.0.1:8000/polls/")
    print('ответ на %s запрос: %s' % (2, res))
    time.sleep(2)
    res = requests.get("http://127.0.0.1:8000/polls/")
    print('ответ на %s запрос: %s' % (3, res))
    res = requests.get("http://127.0.0.1:8000/polls/")
    print('ответ на %s запрос: %s' % (4, res))


send_requests_for_training_cache(CNT_REQUESTS, TIME_OUT)
#send_specific_requests_for_training_cache()