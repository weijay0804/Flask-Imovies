from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

#-------自訂檔案--------
from ..models import User

'''使用者表單'''

class LoginForm(FlaskForm):
    '''使用者登入表單'''
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('保持登入')
    submit = SubmitField('登入', render_kw={'id':'button'})


class RegistrationForm(FlaskForm):
    '''使用者註冊表單'''
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('使用者名稱', validators=[DataRequired(), Length(1, 64), Regexp('[A-Za-z][A-Za-z0-9]*$', 0, '使用者名稱只能含有大小寫英文字母')])
    password = PasswordField('密碼', validators=[DataRequired(), EqualTo('password2', message='密碼必須相同')])
    password2 = PasswordField('再次輸入密碼', validators=[DataRequired()])
    submit = SubmitField('註冊', render_kw={'id':'button'})

    def validate_email(self, field):
        '''檢查email是否存在資料庫裡'''
        if User.query.filter_by(email = field.data).first():
            raise ValidationError('Email已經存在')

    def validate_username(self, field):
        '''檢查username是否存在資料庫裡'''
        if User.query.filter_by(username = field.data).first():
            raise ValidationError('使用者名稱已經存在')


class ChangePasswordForm(FlaskForm):
    '''重設密碼表單'''
    old_password = PasswordField('輸入舊密碼', validators=[DataRequired()])
    password = PasswordField('輸入新密碼', validators=[DataRequired(), EqualTo('password2', message='密碼密須相同')])
    password2 = PasswordField('再次輸入密碼', validators=[DataRequired()])
    submit = SubmitField('變更密碼', render_kw={'id':'button'})


class RestPasswordRequsetForm(FlaskForm):
    '''重新設定密碼請求表單'''
    email = StringField('email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('重設密碼', render_kw={'id':'button'})


class RestPasswordForm(FlaskForm):
    '''重新設定密碼表單'''
    password = PasswordField('輸入新密碼', validators=[DataRequired(), EqualTo('password2', message='密碼必須相等')])
    password2 = PasswordField('再次輸入密碼', validators=[DataRequired()])
    submit = SubmitField('確認', render_kw={'id':'button'})


class ChangeEmailForm(FlaskForm):
    '''重新設定email'''
    email = StringField('新的email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('輸入您的密碼', validators=[DataRequired()])
    submit = SubmitField('確認', render_kw={'id' : 'button'})

    def validate_email(self, field):
        '''確認email是否重複'''
        if User.query.filter_by(email = field.data.lower()).first():
            raise ValidationError('Email 已經被註冊')
