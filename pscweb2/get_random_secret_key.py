from django.core.management.utils import get_random_secret_key
print('SECRET_KEY = \'{0}\''.format(get_random_secret_key()))
