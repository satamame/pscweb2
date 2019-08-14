# 1. Replace the values of SECRET_KEY and DATABASES' PASSWORD
#    with the actual ones.
# 2. Rename this file to 'local_settings.py'.

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '**************************************************'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pscweb2',
        'USER': 'pscweb2',
        'PASSWORD': '***********',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
