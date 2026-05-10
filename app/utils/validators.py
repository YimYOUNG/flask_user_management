import re

def validate_username(username):
    if not username or len(username) < 3 or len(username) > 20:
        return False, "用户名长度必须在3-20个字符之间"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "用户名只能包含字母、数字和下划线"
    return True, None

def validate_email(email):
    if not email:
        return False, "邮箱不能为空"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "邮箱格式不正确"
    if len(email) > 120:
        return False, "邮箱长度不能超过120个字符"
    return True, None

def validate_password(password):
    if not password:
        return False, "密码不能为空"
    if len(password) < 8:
        return False, "密码长度至少8个字符"
    if len(password) > 128:
        return False, "密码长度不能超过128个字符"
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少一个大写字母"
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含至少一个小写字母"
    if not re.search(r'[0-9]', password):
        return False, "密码必须包含至少一个数字"
    return True, None
