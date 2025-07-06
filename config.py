import os
# Для генерации надежного ключа:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_key'
    