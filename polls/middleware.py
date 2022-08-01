import hashlib
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect


def add_field_url_hash(get_response):
    def middleware(request):
        request.url_hash = hashlib.sha256(request.path.encode('utf-8'))
        response = get_response(request)
        return response

    return middleware


class CheckAgreement:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.userprofile.agreement_accepted:
                if not request.path.partition('?next')[0] == reverse('polls:agreement',
                                                                 args=(request.user.id,)):
                    return redirect("%s?next=%s" % (reverse('polls:agreement',
                                                            args=(request.user.id,)), request.path))
        response = self.get_response(request)

        return response
