from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import ( LoginForm, RegistrationForm, ChangePasswordForm,
    RestPasswordRequsetForm, RestPasswordForm, ChangeEmailForm )

#-------自訂檔案--------
from . import auth
from .. import db
from ..models import User, Movie
from ..email import send_email


'''使用者視圖函數'''


@auth.before_app_request
def before_request():
    '''過濾未確認的帳號'''
    if current_user.is_authenticated and not current_user.confiremd \
        and request.blueprint != 'auth' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confiremd:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')



@auth.route('/login', methods = ['GET', 'POST'])
def login():
    '''使用者登入視圖'''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first() #依表單email資料去資料庫撈取使用者

        if user is not None and user.verify_password(form.password.data): #如果使用者不是None和使用者密碼正確，就登入
            login_user(user, form.remember_me.data)
            next = request.args.get('next') #之前想訪問的視圖涵式

            if next is None or not next.startswith('/'): #確保next裡的url是相對url
                next = url_for('main.index')

            return redirect(next) 
        flash('錯誤的使用者名稱或密碼')
        
    return render_template('auth/login.html', form = form)


@auth.route('/logout')
@login_required
def logout():
    '''使用者登出視圖'''
    logout_user()
    flash('你已成功登出')
    return redirect(url_for('main.index'))

@auth.route('/registration', methods = ['GET', 'POST'])
def registration():
    '''使用者註測視圖'''
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data, username = form.username.data,
                    password = form.password.data)

        db.session.add(user)
        db.session.commit()
        token = user.gengerate_confirmation_token()
        send_email(user.email, '確認你的帳號', 'auth/email/confirm', user = user, token = token)
        flash('認證信件已經送到你的信箱')

        return redirect(url_for('main.index'))
    
    return render_template('auth/registration.html', form = form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    '''確認使用者帳號視圖'''
    if current_user.confiremd:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('您已經成功認證帳號')
    else:
        flash('此認證連結已失效或逾時')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    '''重新寄帳號認證email視圖'''
    token = current_user.gengerate_confirmation_token()
    send_email(current_user.email, '確認你的帳號', 'auth/email/confirm', user = current_user, token = token)
    flash('新的認證信件已經送到你的信箱')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods = ['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('您的密碼變更成功')
            return redirect(url_for('main.index'))
        else:
            flash('密碼錯誤')
    return render_template('auth/change_password.html', form = form)

@auth.route('/reset-password', methods = ['GET', 'POST'])
def password_rest_requset():
    '''重新設定密碼請求視圖'''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = RestPasswordRequsetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            token = user.generate_reset_passsword_token()
            send_email(user.email, '重新設定您的密碼',
                        'auth/email/reset_password',
                        user = user, token = token )
        flash('確認信件已寄到您的email')

        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form = form)


@auth.route('/reset-password/<token>', methods = ['GET', 'POST'])
def password_reset(token):
    '''重新設定密碼視圖'''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = RestPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('您的密碼已經成功變更')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form = form)


@auth.route('/change-email/', methods = ['GET', 'POST'])
@login_required
def change_email_requset():
    '''更改email請求視圖'''
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_change_email_token(new_email)
            send_email(new_email, '確認您的新eamil', 'auth/email/change_email', user = current_user, token = token)
            flash('確認信件已送至您的信箱')
            return redirect(url_for('main.index'))
        else:
            flash('錯誤的密碼或帳號')
    return render_template('auth/change_email.html', form = form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    '''更改email視圖'''
    if current_user.change_email(token):
        db.session.commit()
        flash('您的email已經更改完成')
    else:
        flash('不允許的請求')
    return redirect(url_for('main.index'))




