import hashlib
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.http import HttpResponse
from datetime import datetime as dt

LIMIT_REQUESTS = 5
TIME_OUT = 10
TIME_BLOCK = 60*60

class FilterIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_key = str(hash(request.META['REMOTE_ADDR']))
        block_key = ip_key + 'block'
        time_key = ip_key + 'time'
        if cache.get(block_key):
            return HttpResponse(status='429')
        cnt_requests = cache.get(ip_key)
        if cnt_requests:
            start_time = cache.get(time_key)
            delta = (dt.now() - start_time).total_seconds()
            if delta <= TIME_OUT and cnt_requests >= LIMIT_REQUESTS:
                print('попався')
                cache.delete_many([ip_key, time_key])
                cache.add(block_key, '', TIME_BLOCK)
            elif delta > TIME_OUT:
                cache.delete_many([ip_key, time_key])
            else:
                cache.incr(ip_key, 1)
        else:
            cache.add(time_key, dt.now())
            cache.add(ip_key, 1)

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
