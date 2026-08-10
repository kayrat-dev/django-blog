from .base import *

# На сервере отладка КАТЕГОРИЧЕСКИ запрещена
DEBUG = False

# Домен твоего будущего сервера (можно вынести в .env)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['yourdomain.com'])