import hashlib
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.http import HttpResponse
from datetime import datetime as dt
from django.db import transaction

import logging


LIMIT_REQUESTS = 3
TIME_OUT = 5
MAX_FREQUENCY = LIMIT_REQUESTS/TIME_OUT
TIME_BLOCK = 60*60


block_logger = logging.getLogger('block_logger')
block_handler = logging.FileHandler('block.log')
block_handler.setLevel(logging.INFO)
block_logger.addHandler(block_handler)


class FilterIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_key = str(request.META['REMOTE_ADDR'])
        block_key = ip_key + 'block'
        info_tuple_key = ip_key + 'info'
        if cache.get(block_key):
            block_logger.info('The following ip address is blocked:' + ip_key)
            return HttpResponse(status='429')
        cnt_requests = cache.get(ip_key)

        with transaction.atomic():
            if cnt_requests:
                cnt_delta = cnt_requests
                between_mean, past_time = cache.get(info_tuple_key)
                now = dt.now()
                delta = (now - past_time).total_seconds()
                between_mean = (between_mean*(cnt_delta-1) + delta)/cnt_delta
                frequency = 1/between_mean

                cache.incr(ip_key, 1)
                info_tuple = (between_mean, now)
                cache.set(info_tuple_key, info_tuple)

                if cnt_requests >= LIMIT_REQUESTS*3:
                    cache.decr(ip_key, LIMIT_REQUESTS)

                if cnt_requests >= LIMIT_REQUESTS and frequency > MAX_FREQUENCY:
                    cache.delete_many([ip_key, info_tuple_key])
                    cache.add(block_key, 'block', TIME_BLOCK)
                    return HttpResponse(status='429')
            else:
                cache.add(ip_key, 1)
                info_tuple = (0, dt.now())
                cache.set(info_tuple_key, info_tuple)

        response = self.get_response(request)
        return response


def add_field_url_hash(get_response):
    def middleware(request):
        request.url_hash = hashlib.sha256(request.path.encode('utf-8'))
        response = get_response(request)
        return response

    return middleware


class AuthMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if not request.user.is_authenticated:
            user = authenticate(request)
            if user:
                request.user = user
        response = self.get_response(request)
        return response


class CheckAgreement:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.userprofile.agreement_accepted:
                url_agreement = reverse('polls:agreement', args=(request.user.userprofile.id,))
                if not request.path.partition('?next')[0] == url_agreement:
                    return redirect("%s?next=%s" % (url_agreement, request.path))
        response = self.get_response(request)

        return response
