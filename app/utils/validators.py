import re

def validate_username(username):
    """Valida o formato do nome de usuário"""
    return 3 <= len(username) <= 20 and re.match(r'^\w+$', username)

def validate_password(password):
    """Valida a força da senha"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[^A-Za-z0-9]', password):
        return False
    return True