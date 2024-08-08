from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField,
                     TimeField)
from wtforms.validators import DataRequired, EqualTo, Length

class UserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите Пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add User')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Авторизоваться')

class StyleForm (FlaskForm):
    stylename = StringField('Название стиля', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Добавить')

class TeacherForm (FlaskForm):
    teacherFIO = StringField('ФИО преподавателя', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Добавить')

class TeacherStyleForm (FlaskForm):
    teacherStyle = SelectField('Назначить стиль преподавателю', validators=[DataRequired()])
    submit = SubmitField('Добавить стиль преподавателю')

class LessonForm (FlaskForm):
    teacherFIO = SelectField('Назначить преподавателя', validators=[DataRequired()])
    styleName = SelectField('Назначить стиль', validators=[DataRequired()])
    date = DateField('Назначить дату', validators=[DataRequired()])
    time = TimeField('Назначить время', validators=[DataRequired()])
    submit = SubmitField('Добавить занятие')

class RecordLessonForm (FlaskForm):
    submit = SubmitField('Записаться на занятие')
