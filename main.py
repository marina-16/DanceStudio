from app import app, models

if __name__ == '__main__':
    with app.app_context():
        models.create_tables()
    app.run()