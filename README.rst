=====
Polls (and training)
=====

Основное приложение — это опросы из туториала по django.
Далее выполнены задания по изучению django:

1. Менеджеры::
    1. Сделать менеджер для модели Question который который который имеет метод all_questoions - возвращающий кол-во вопросов
    2. В менеджере сделать метод annotate_votes() который добавляет votes_cnt
    3. Сделать тоже что и в пунктах 1 и 2, но менеджер сделать на основе Queryset
    4. Сделать функцию которая атормарно увидичивает votes для Choice  на 1
    5. Сделать в менеджере Questions функцию filter_ab которая возвращется все Question у которых текст начинается либо на "a" либо на "b"

2. Management command и транзакции::
    1. Написать management команду которая принимает в качестве агрумента id Choice, получает choice  из бд, выполняет sleep на 60 секунд
    потом делает choice.vote += 1 и choice.save()
    Запустить два теримнала и в обоих запустить эту команду для одного и того же choice
    Посмотреть на сколько реально увеличился choice.votes после завершения работы обоих команд
    2. Модифицировать алгоритм через F-object и update и убедиться, что это решает проблему
    3. Модифицировать алгоритм через select_for_update и transation.atomic() и убедится что это тоже решает проблему

3. Транзакции и формы::
    1. Нужно добавить модель AuthorBalance со значение balance - сколько денег на счету автора опроса
    2. Для каждого автора баланс по умочанию - 0
    3. Менеджер в админке может менять баланс любого автора
    4. сделать форму, отдельную от админке, в которой можно пополнить или списать сумму с баланса автора. При этом, при попытке списать сумму большую, чем есть на балансе - выдавать ошибку.

4. Наследование::
    1. Для нашего приложения нужно ввести систему тарификации для авторов.
    2. У каждого автора должен быть один тариф
    3. Тарифы могут быть двух типов:
     - постоянная фикисрованная цена
    - цена зависит от кол-во вопросов, которое создал автор по формуле x*кол-во вопросов, где x - хранится в тарифе
    4. Администратор может создавать тарифы двух типов
    5. Администратор может назначить автору тариф и настроить его по одному из типов.
    6. В админке авторов выводить колону с текущей ценой на основе тарифа автора
    7. найти популярный, поддерживаемый пакет  для django, который упрощает работу с наследуемыми моделями подобно нашему решению и заюзать его

5. Формы::
    Нужно сделать аналог страницы создания и редактирования Question. На странице должно быть возможно изменить поля Question и также список вопросов.

6. Middleware::
    1. Нужно сделать так, чтобы переменной request каждого запроса присуствовало поле url_hash - которое вычисляется как sha256 хеш текущего улра
    2. Сделать модель - Профиль пользователя. профиль автотматически создается для каждого пользователя. И для существующих тоже. В профиле есть поле - agreement_accepted, по умолчанию = False
    3. Сделать так, что если текущий пользователь еще не имеет agreement_accepted==True, то он попадает на страницу соглашения с условиями

7. JWT::
    1. Прочитать что такое jwt и сделать свой бекенд авторизации на основе данных jwt

8. Кеш::
    0. Написать функцию Которая делает sleep на 5 секунд и возращет 'ОК'
    1. Написать вьюху, которая вычисляет возвращает "ОК" через 5 секунд (через time.sleep)
    2. Включить кеширование в проекте. В качестве бекенда заюзать Базу данных
    3. Обернуть данную функцию в кеширующий декоратор, убедться, что работает быстрее чем за 5 секунд
    4. Вместо декоратора, заюзай получение значения из кеша внутри функции: Если в кеше есть значение - вернуть его, если нет - сначала 5 секунд sleep, потом вернуть значение
    Время жизни кеша - 1 минут

    Часть 2:
    1. Нужно если в течении 30 секунд приходит более 10 запросов с одного и того же ip адреса блокировать запросы с этого адреса в течении часа

9. Conditional View Processing::
    1. Кешировать страницу со списком опросов на стооне клиента

10. Логирование:
    1. Выводить все сообщения уровня DEBUG в файл debug.log с ротацией каждый час
    2. Добавить в логирование работы блокирующего мидлваря - чтобы в логе было видно какой ip адрес заблокирован. Выводить в отдельный файл лога. Уровень логгирования: info

11. Крипто подписи::
    1. Сделать вьюху, которая принимает данные для изменения одной из моделей (Question). Данные принимаются в формате json
    2. Вьюха должна работать без автризации
    3. Сделать так, чтобы вызвать данную вьюху могли только доверенные участники

12. Конфигурирование приложения через переменные окружения::
    1. Переделать весь конфиг приложения settings.py таким образом, чтобы можно было все настройки, которые критичны, такие как база данных и прочее, т.е. зависящие от контекста, хоста, можно было передать через переменные окружения;
    2. Если через переменные окружения ничего не передано, то должно работать как будто на локал хосте;
    3. Добавить файл app_env_example, чтобы другому разработчику легко было понять, какие должны быть настройки в переменных окружения.

13. Celery::
    1. Написать вьюху, которая вычисляет 2+2, но делает это через таск.
    Цели задания: научиться создавать таски, ставить их в очередь,  а также подключать воркеров к очереди отдельным процессом и смотреть, как они работают

Quick (maybe) start
-----------
In settings.py:

    0. Add import config:

        from decouple import config

    1. Add "polls" to your INSTALLED_APPS setting like this::

        INSTALLED_APPS = [
            ...
            'polymorphic',
            'polls',
            'receiver',
            'crispy_forms',
            'dynamic_formsets',
        ]

    2. Add to your MIDDLEWARE::
        MIDDLEWARE = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.auth.middleware.RemoteUserMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',

            'django.middleware.http.ConditionalGetMiddleware',

            'polls.middleware.AuthMiddleWare',
            'polls.middleware.FilterIPMiddleware',
            'polls.middleware.add_field_url_hash',
            'polls.middleware.CheckAgreement',

        ]

    3. Add  AUTHENTICATION_BACKENDS:
        AUTHENTICATION_BACKENDS = [
            'polls.backends.UserProfileBackend',
            'django.contrib.auth.backends.ModelBackend',
        ]

    4. Add CACHES:
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
                'LOCATION': 'my_cache_table',
            }
        }

    5. Add LOGGING:
        LOGGING = {
            'version': 1,                       # the dictConfig format version
            'disable_existing_loggers': False,  # retain the default loggers

            'handlers': {
                'log_file': {
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': 'debug.log',
                    'level': 'DEBUG',
                    'when': 'H',
                    'interval': 1,
                },
                'block_file': {
                    'class': 'logging.FileHandler',
                    'filename': 'block.log',
                    'level': 'INFO',
                },
            },

            'loggers': {
                '': {
                    'level': 'DEBUG',
                    'handlers': ['log_file', 'block_file'],
                },
            },

            'formatters': {
                'verbose': {
                    'format': '{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname} {message}',
                    'style': '{',
                },
            },
        }

    6. ADD CELERY:
        CELERY_BROKER_URL = config('CELERY_BROKER_URL')
        CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')


2. Include the polls URLconf in your project urls.py like this::

    path('polls/', include('polls.urls')),

3. Run ``python manage.py migrate`` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/polls/ to participate in the poll.

6. The author_changed signal is written, which responds to a change in the Author field in the Question.

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
