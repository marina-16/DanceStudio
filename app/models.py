from app import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            password VARCHAR NOT NULL,
            administrator bool
        );
    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS style (
                id SERIAL PRIMARY KEY,
                name VARCHAR(80) NOT NULL,
                description VARCHAR(120) NOT NULL
            );
        ''')
    cursor.execute('''
               CREATE TABLE IF NOT EXISTS teacher (
                   id SERIAL PRIMARY KEY,
                   FIO VARCHAR(80) NOT NULL,
                   description VARCHAR(120) NOT NULL
               );
           ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS teacher_style (
                       teacher_id INTEGER,
                       style_id INTEGER,
                       FOREIGN KEY (teacher_id) REFERENCES teacher (id),
                       FOREIGN KEY (style_id) REFERENCES style (id)
                   );
               ''')
    cursor.execute('''
                       CREATE TABLE IF NOT EXISTS lesson (
                           id SERIAL PRIMARY KEY,
                           date DATE NOT NULL,
                           time TIME NOT NULL,
                           teacher_id INTEGER REFERENCES teacher (id) NOT NULL,
                           style_id INTEGER REFERENCES style (id) NOT NULL
                       );
                   ''')
    cursor.execute('''
                       CREATE TABLE IF NOT EXISTS user_lesson (
                           user_id INTEGER,
                           lesson_id INTEGER,
                           FOREIGN KEY (user_id) REFERENCES users (id),
                           FOREIGN KEY (lesson_id) REFERENCES lesson (id)
                       );
                   ''')
    conn.commit()
    cursor.close()
    conn.close()


class Users(UserMixin):
    def __init__(self, id, username, password, administrator=False):
        #шаблон
        self.id = id
        self.username = username
        self.password = password
        self.administrator = administrator

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, administrator) VALUES (%s, %s, %s) RETURNING id;",
            (self.username, self.password, self.administrator)
        )
        self.id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users;')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users

    def is_administrator(self):
        return self.administrator

    def is_username_unique(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = %s;', (self.username,))
        count = cursor.fetchone()[0] #кол-во
        cursor.close()
        conn.close()
        return count == 0

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, passw):
        return check_password_hash(self.password, passw)

    @staticmethod
    def get_by_id(user_id):
        try:
            user_id = int(user_id)
        except ValueError:
            return None

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s;', (user_id,))
        user_data = cursor.fetchone() #для одного пользователя
        cursor.close()
        conn.close()

        if user_data:
            return Users(*user_data)
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s;', (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            return Users(*user_data)
        return None

    def update_admin(self, new_admin):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET administrator = %s WHERE username = %s RETURNING id;',
                       (new_admin, self.username))
        updated_user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return updated_user_id

class Style:
    def __init__(self, name, description, id=None):
        self.id = id
        self.name = name
        self.description = description

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO style (name, description) VALUES (%s, %s) RETURNING id;",
            (self.name, self.description)
        )
        self.id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all_styles():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM style;')
        styles = cursor.fetchall()
        cursor.close()
        conn.close()
        return styles

    def is_name_unique(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM style WHERE name = %s;', (self.name,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count == 0

    @staticmethod
    def get_by_name(stylename):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM style WHERE name = %s;', (stylename,))
        style_data = cursor.fetchone()
        cursor.close()
        conn.close()
        # id = style_data[0]
        # stylename = style_data[1]
        # description = style_data[2]
        if style_data:
            id, stylename, description = style_data
            return Style(stylename, description, id)
        return None

    @staticmethod
    def get_style_name_by_id(style_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM style WHERE id = %s;', (style_id,))
        style_name = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return style_name

    def update(self):
        if not self.id:
            # Если id не задан, обновление невозможно
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE style SET name = %s, description = %s WHERE id = %s;",
            (self.name, self.description, self.id)
        )
        conn.commit()
        cursor.close()
        conn.close()


@login.user_loader
def load_user(user_id):
    return Users.get_by_id(user_id)


class Teacher:
    def __init__(self, FIO, description, id=None):
        self.id = id
        self.FIO = FIO
        self.description = description

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO teacher (FIO, description) VALUES (%s, %s) RETURNING id;",
            (self.FIO, self.description)
        )
        self.id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all_teacher():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teacher;')
        teachers = cursor.fetchall()
        cursor.close()
        conn.close()
        return teachers

    def is_FIO_unique(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM teacher WHERE FIO = %s;', (self.FIO,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count == 0

    @staticmethod
    def get_by_name(teachername):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teacher WHERE FIO = %s;', (teachername,))
        teacher_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if teacher_data:
            id, FIO, description = teacher_data
            return Teacher(FIO, description, id)
        return None

    @staticmethod
    def get_teacher_name_by_id(teacher_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT FIO FROM teacher WHERE id = %s;', (teacher_id,))
        teacher_name = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return teacher_name

    def update(self):
        if not self.id:
            # Если id не задан, обновление невозможно
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE teacher SET FIO = %s, description = %s WHERE id = %s;",
            (self.FIO, self.description, self.id)
        )
        conn.commit()
        cursor.close()
        conn.close()

class Teacher_style:
    def __init__(self, teacherID, styleID):
        self.teacherID = teacherID
        self.styleID = styleID

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO teacher_style (teacher_id, style_id) VALUES (%s, %s);",
            (self.teacherID, self.styleID)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_styles_for_teacher(id_teacher):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT style_id FROM teacher_style WHERE teacher_id = %s;', (id_teacher,))
        styles = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return styles

    @staticmethod
    def get_style_names(style_ids):
        if not style_ids:
            return []
        conn = get_db()
        cursor = conn.cursor()
        # плейсхолдеры для всех элементов style_ids
        placeholders = ', '.join(['%s' for _ in style_ids])
        # выбор строк, у которых id находится в списке style_ids
        cursor.execute(f'SELECT id, name FROM style WHERE id IN ({placeholders});', style_ids)
        style_results = cursor.fetchall()
        cursor.close()
        conn.close()

        # словарь (id стиля-название)
        style_dict = {style_id: style_name for style_id, style_name in style_results}
        return style_results

    @staticmethod
    def is_TeacherStyle_unique(teacher_id, style_id):
        conn = get_db()
        cursor = conn.cursor()
        # Проверка есть ли уже такой стиль у данного преподавателя
        cursor.execute('SELECT COUNT(*) FROM teacher_style WHERE teacher_id = %s AND style_id = %s;',
                       (teacher_id, style_id))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count == 0


class Lesson:
    def __init__(self, date, time, teacher_id, style_id, id=None):
        self.id = id
        self.date = date
        self.time = time
        self.teacher_id = teacher_id
        self.style_id = style_id

    # save все
    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lesson (date, time, teacher_id, style_id) VALUES (%s, %s, %s, %s) RETURNING id;",
                       (self.date, self.time, self.teacher_id, self.style_id))
        self.id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all_lessons():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lesson;')
        lessons = cursor.fetchall()
        cursor.close()
        conn.close()
        return lessons

    @staticmethod
    def is_lesson_unique(date, time, teacher_id):
        conn = get_db()
        cursor = conn.cursor()
        # проверка есть ли уже урок с такой же датой, временем и учителем
        cursor.execute('SELECT COUNT(*) FROM lesson WHERE date = %s AND time = %s AND teacher_id = %s;',
                       (date, time, teacher_id))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count == 0

    @staticmethod
    def get_lesson_by_id(lesson_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lesson WHERE id = %s;', (lesson_id,))
        lesson_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if lesson_data:
            id, date, time, teacher_id, style_id = lesson_data
            return Lesson(date, time, teacher_id, style_id, id)
        return None

    def update(self):
        if not self.id:
            # Если id не задан, обновление невозможно
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE lesson SET date = %s, time = %s, teacher_id = %s, style_id = %s WHERE id = %s;",
            (self.date, self.time, self.teacher_id, self.style_id, self.id)
        )
        conn.commit()
        cursor.close()
        conn.close()


class User_lesson:
    def __init__(self, userID, lessonID):
        self.userID = userID
        self.lessonID = lessonID

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_lesson (user_id, lesson_id) VALUES (%s, %s);",
            (self.userID, self.lessonID))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def is_user_registered_for_lesson(userID, lessonID):
        if not lessonID:
            # когда lessonID не задан
            return False
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM user_lesson WHERE user_id = %s AND lesson_id = %s;",
            (userID, lessonID)
        )
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0

