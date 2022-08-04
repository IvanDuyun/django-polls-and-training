=====
Polls
=====

Polls is a Django app to conduct web-based polls. For each question,
visitors can choose between a fixed number of answers.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'polymorphic',
        'polls',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('polls/', include('polls.urls')),

3. Run ``python manage.py migrate`` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/polls/ to participate in the poll.

6. The author_changed signal is written, which responds to a change in the Author field in the Question.

7. Add to your AUTHENTICATION_BACKENDS setting like this::

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'polls.backends.UserProfileBackend',
    ]

8. To connect a signal, you need to create a receivers.py file in the application with writing a connection to the signal.
In the apps.py of the application, write the def ready () method with the import of the receivers.py file. See example below:

-----------
receivers.py:
from django.dispatch import receiver
from polls import signals


@receiver(signals.author_changed)
def my_task_done(sender, **kwargs):
    print('Сигнал принял: автор изменился')
-----------
apps.py:
from django.apps import AppConfig


class ReceiverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'receiver'

    def ready(self):
        from . import receivers
