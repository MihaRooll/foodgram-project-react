import os

from django.core.wsgi import get_wsgi_application

# Установка значения по умолчанию для переменной среды DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

# Получение WSGI-приложения
application = get_wsgi_application()
