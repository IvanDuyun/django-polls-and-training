import hashlib
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.http import HttpResponse
from datetime import datetime as dt
from django.db import transaction


LIMIT_REQUESTS = 3
TIME_OUT = 5
TIME_BLOCK = 60*60


class FilterIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_key = str(hash(request.META['REMOTE_ADDR']))
        block_key = ip_key + 'block'
        past_time_key = ip_key + 'time'
        between_mean_key = ip_key + 'between_mean'
        if cache.get(block_key):
            return HttpResponse(status='429')
        cnt_requests = cache.get(ip_key)

        with transaction.atomic():
            if cnt_requests:
                cnt_delta = cnt_requests+1
                past_time = cache.get(past_time_key)
                between_mean = cache.get(between_mean_key)
                now = dt.now()
                delta = (now - past_time).total_seconds()
                between_mean = (between_mean*(cnt_delta-1) + delta)/cnt_delta
                frequency = 1/between_mean

                cache.incr(ip_key, 1)
                cache.set(past_time_key, now)
                cache.set(between_mean_key, between_mean)

                if cnt_requests >= LIMIT_REQUESTS*3:
                    cache.decr(ip_key, LIMIT_REQUESTS)

                if cnt_requests >= LIMIT_REQUESTS and frequency > LIMIT_REQUESTS/TIME_OUT:
                    cache.delete_many([ip_key, past_time_key, between_mean_key])
                    cache.add(block_key, 'block', TIME_BLOCK)
                    return HttpResponse(status='429')
            else:
                cache.add(ip_key, 1)
                cache.add(between_mean_key, 0)
                cache.add(past_time_key, dt.now())

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
