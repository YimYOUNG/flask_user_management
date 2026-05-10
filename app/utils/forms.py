from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.utils.validators import validate_username, validate_email, validate_password

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址'),
        Length(max=120, message='邮箱长度不能超过120个字符')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=8, max=128, message='密码长度必须在8-128个字符之间')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册')

    def validate_username(self, username):
        is_valid, error_msg = validate_username(username.data)
        if not is_valid:
            raise ValidationError(error_msg)

    def validate_email(self, email):
        is_valid, error_msg = validate_email(email.data)
        if not is_valid:
            raise ValidationError(error_msg)

    def validate_password(self, password):
        is_valid, error_msg = validate_password(password.data)
        if not is_valid:
            raise ValidationError(error_msg)

class LoginForm(FlaskForm):
    username = StringField('用户名/邮箱', validators=[
        DataRequired(message='请输入用户名或邮箱')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码')
    ])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class UserEditForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址'),
        Length(max=120, message='邮箱长度不能超过120个字符')
    ])
    is_admin = BooleanField('管理员')
    is_active = BooleanField('激活')
    submit = SubmitField('保存')
