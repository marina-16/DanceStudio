from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def custom_login_required(func):
    @wraps(func)
    def login_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, войдите в систему, чтобы просмотреть эту страницу', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return login_view

def admin_required(func):
    @wraps(func)
    def admin(*args, **kwargs):
        if current_user.is_authenticated and current_user.administrator:
            #если пользователь аутентифицирован и является администратором
            return func(*args, **kwargs)
        else:
            flash('Вы не администратор сайта')
            return redirect(url_for('index'))
    return admin