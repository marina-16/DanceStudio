from app import app
from app.models import Users, create_tables, Style, Teacher, Teacher_style, Lesson, User_lesson
from flask import render_template, request, redirect, url_for, flash
from app.forms import *
from flask_login import login_user, logout_user, current_user, login_required
from app.decorators import custom_login_required, admin_required

@app.route('/')
def index():
     users = Users.get_all()
     return render_template('index.html', users=users)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    id = None
    password = None
    admin_user = Users(id, 'admin', password, True)
    admin_user.set_password('admin')
    if admin_user.is_username_unique():
        admin_user.save()
        print('Админ создан')
    else:
        print('Админ уже есть в бд')

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        id=None
        password = None
        new_user = Users(id, username, password)
        new_user.set_password(form.password.data)
        if new_user.is_username_unique():
            new_user.save()
            login_user(new_user) #новый пользователь авторизован
            flash('Пользователь успешно добавлен', 'success')
            return redirect(url_for('index'))
        else:
            flash('Имя пользователя уже существует', 'error')

    return render_template('registration.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.get_by_username(form.username.data)
        if user:
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Вход выполнен успешно', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверный пароль', 'error')
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html', form=form)

@app.route('/logout')
@custom_login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('login'))

@app.route ('/addstyle', methods=['GET', 'POST'])
@admin_required
def addstyle ():
    form = StyleForm()

    if form.validate_on_submit():
        new_style = Style(name=form.stylename.data, description=form.description.data)
        if new_style.is_name_unique():
            new_style.save()
            flash('Стиль успешно добавлен', 'success')
            return redirect(url_for('index'))
        else:
            flash('Такой стиль уже существует')

    return render_template('add_style.html', form=form)

@app.route ('/addteacher', methods=['GET', 'POST'])
@admin_required
def addteacher ():
    form = TeacherForm()

    if form.validate_on_submit():
        #инициализация класса
        new_teacher = Teacher(FIO=form.teacherFIO.data, description=form.description.data)
        if new_teacher.is_FIO_unique():
            new_teacher.save()
            flash('Преподаватель успешно добавлен', 'success')
            return redirect(url_for('index'))
        else:
            flash('Такой преподаватель уже существует')

    return render_template('add_teacher.html', form=form)

@app.route('/teachers')
def view_teachers():
    teachers = Teacher.get_all_teacher()
    return render_template('view_teacher.html', teachers=teachers)

@app.route ('/editteacher/<id>', methods=['GET', 'POST'])
@admin_required
def editteacher (id):
    teacher_name = Teacher.get_teacher_name_by_id(id)
    teacher = Teacher.get_by_name(teacher_name)
    form = TeacherForm()
    form.submit.label.text = 'Изменить'
    #изначальные данные
    form.teacherFIO.data = teacher.FIO
    form.description.data = teacher.description
    if form.validate_on_submit():
        teacher_edit = Teacher(
            id=id,
            FIO=request.form.get('teacherFIO'),
            description=request.form.get('description')
        )
        if teacher.FIO != teacher_edit.FIO:
            if teacher_edit.is_FIO_unique():
                teacher_edit.update()
                flash('Преподаватель успешно отредактирован', 'success')
                return redirect(url_for('view_teachers'))
            else:
                flash('Такой преподаватель уже существует')
        elif teacher_edit.description != teacher.description:
            teacher_edit.update()
            flash('Преподаватель успешно отредактирован', 'success')
            return redirect(url_for('view_teachers'))
        else:
            flash('Вы ничего не изменили', 'success')

    return render_template('edit_teacher.html', form=form)

@app.route('/infoteacher/<id>')
def infoteacher(id):
    ids_styles= Teacher_style.get_styles_for_teacher(id)
    styles_names=Teacher_style.get_style_names(ids_styles)
    return render_template('view_styles_teacher.html', styles=styles_names, id=id)

@app.route ('/addstyleteacher/<id>', methods=['GET', 'POST'])
@admin_required
def addstyleteacher(id):
    ids_styles = Teacher_style.get_styles_for_teacher(id)
    styles_names = Teacher_style.get_style_names(ids_styles)
    form = TeacherStyleForm()
    styles = Style.get_all_styles()
    style = []
    names = [i[1] for i in styles_names]
    for i in styles:
         if i[1] not in names:
             style.append(i[1])

    form.teacherStyle.choices = style

    if form.validate_on_submit():
        new_style = Style.get_by_name(form.teacherStyle.data)
        style_for_teacher = Teacher_style(teacherID=id, styleID=new_style.id)
        if style_for_teacher.is_TeacherStyle_unique(id, new_style.id):
            style_for_teacher.save()
            flash('Стиль для преподавателя успешно добавлен', 'success')
            return redirect(url_for('infoteacher', id = str(id)))
        else:
            flash('Такой стиль уже существует')

    return render_template('add_style_teacher.html', form=form)

@app.route ('/addlesson', methods=['GET', 'POST'])
@admin_required
def addlesson ():
    form = LessonForm()

    form.teacherFIO.choices = [teacher[1] for teacher in Teacher.get_all_teacher()]#помещаем в SelectField
    form.styleName.choices = [style[1] for style in Style.get_all_styles()]

    if form.validate_on_submit():
        teacher = Teacher.get_by_name (form.teacherFIO.data)

        style = Style.get_by_name (form.styleName.data)
        date = form.date.data
        time = form.time.data
        new_lesson = Lesson (date=date, time=time, teacher_id=teacher.id, style_id=style.id)
        if new_lesson.is_lesson_unique(date, time, teacher.id):
            new_lesson.save()
            flash('Занятие успешно добавлено', 'success')
            return redirect(url_for('view_lessons'))
        else:
            flash('Такое занятие уже существует')


    return render_template('add_lesson.html', form=form)

@app.route('/lesson', methods=['GET', 'POST'])
def view_lessons():
    form = RecordLessonForm()
    lessons = Lesson.get_all_lessons()
    formatted_lessons = [] #список

    for lesson in lessons:
        teacher_name = Teacher.get_teacher_name_by_id(lesson[3]) #из каждой строки, которые находятся в списке, берем третье значение
        style_name = Style.get_style_name_by_id(lesson[4])

        formatted_lesson = {
            'teacher_name': teacher_name,
            'style_name': style_name,
            'date': lesson[1],
            'time': lesson[2],
            'id': lesson[0],
        }
        formatted_lessons.append(formatted_lesson)

    if form.validate_on_submit():
        lesson_id = request.form['lesson_id']
        user_id = current_user.id
        if not User_lesson.is_user_registered_for_lesson(user_id, lesson_id):
            user_lesson = User_lesson(userID=user_id, lessonID=lesson_id)
            user_lesson.save()
            flash('Вы успешно записались на занятие', 'success')

            return redirect(url_for('index'))
        else:
            flash('Вы уже записаны на это занятие', 'error')
            return redirect(url_for('index'))


    return render_template('view_lessons.html', lessons=formatted_lessons, form=form)

@app.route ('/editlesson/<id>', methods=['GET', 'POST'])
@admin_required
def editlesson(id):
    lesson = Lesson.get_lesson_by_id(id)
    teacher_name = Teacher.get_teacher_name_by_id(lesson.teacher_id)
    style_name = Style.get_style_name_by_id(lesson.style_id)
    form = LessonForm(teacherFIO=teacher_name, styleName=style_name)
    form.submit.label.text = 'Изменить'

    form.teacherFIO.choices = [teacher[1] for teacher in Teacher.get_all_teacher()]
    form.styleName.choices = [style[1] for style in Style.get_all_styles()]

    if form.validate_on_submit():
        teacher = Teacher.get_by_name(form.teacherFIO.data)
        style = Style.get_by_name(form.styleName.data)
        #новые значения
        lesson_edit = Lesson(
            id=id,
            date=request.form.get('date'),
            time=request.form.get('time'),
            teacher_id=teacher.id,
            style_id=style.id,
        )

        if lesson.date != lesson_edit.date:
            if lesson_edit.is_lesson_unique(date=request.form.get('date'), time=request.form.get('time'), teacher_id=teacher.id):
                lesson_edit.update()
                flash('Занятие успешно отредактировано', 'success')
                return redirect(url_for('view_lessons'))
            else:
                flash('Такое занятие уже существует')
        elif lesson_edit.time != lesson.time:
            lesson_edit.update()
            flash('Преподаватель успешно отредактирован', 'success')
            return redirect(url_for('view_lessons'))
        elif lesson_edit.teacher_id != lesson.teacher_id:
            lesson_edit.update()
            flash('Занятие успешно отредактировано', 'success')
            return redirect(url_for('view_lessons'))
        elif lesson_edit.style_id != lesson.style_id:
            lesson_edit.update()
            flash('Занятие успешно отредактировано', 'success')
            return redirect(url_for('view_lessons'))
        else:
            flash('Вы ничего не изменили', 'success')

    return render_template('edit_lesson.html', form=form, lesson=lesson, nameT=teacher_name, nameS=style_name)

@app.route('/styles')
def view_styles():
    styles = Style.get_all_styles()
    return render_template('view_styles.html', styles=styles)

@app.route('/addadmin/<id>')
@custom_login_required
def addadmin(id):
    user = Users.get_by_id(id)
    user.update_admin(True)
    flash('Новый администратор добавлен', 'success')
    return redirect(url_for('index'))

@app.route ('/editstyle/<id>', methods=['GET', 'POST'])
@admin_required
def editstyle (id):
    style_name = Style.get_style_name_by_id(id)
    style = Style.get_by_name(style_name)
    form = StyleForm()
    form.submit.label.text = 'Изменить'
    form.stylename.data = style.name
    form.description.data = style.description
    if form.validate_on_submit():
        style_edit = Style(
            id=id,
            name=request.form.get('stylename'),
            description=request.form.get('description')
        )
        if style.name != style_edit.name:
            if style_edit.is_name_unique():
                style_edit.update()
                flash('Стиль успешно отредактирован', 'success')
                return redirect(url_for('view_styles'))
            else:
                flash('Такой стиль уже существует')
        elif style_edit.description != style.description:
            style_edit.update()
            flash('Стиль успешно отредактирован', 'success')
            return redirect(url_for('view_styles'))
        else:
            flash('Вы ничего не изменили', 'success')

    return render_template('edit_style.html', form=form)