import psycopg2

class DatabaseManager:
    def __init__(self, db_name, user, password, host='localhost', port='5432'):
        self.connection = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()

    def add_user(self, username):
        try:
            self.cursor.execute(
                "INSERT INTO public.users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING;",
                (username,)
            )
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при добавлении пользователя в БД: {e}")
            self.connection.rollback()

    def update_user_location(self, username, latitude, longitude):
        try:
            self.cursor.execute(
                "UPDATE public.users SET latitude = %s, longitude = %s WHERE username = %s;",
                (latitude, longitude, username)
            )
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при обновлении геолокации пользователя в БД: {e}")
            self.connection.rollback()

    def get_user_location(self, username):
        try:
            self.cursor.execute(
                "SELECT latitude, longitude FROM public.users WHERE username = %s;",
                (username,)
            )
            result = self.cursor.fetchone()
            return result if result else None
        except Exception as e:
            print(f"Ошибка при получении геолокации пользователя из БД: {e}")
            return None

    def close(self):
        self.cursor.close()
        self.connection.close()


    def get_all_users(self):
        try:
            self.cursor.execute("SELECT * FROM users;")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении списка пользователей: {e}")
            return []
