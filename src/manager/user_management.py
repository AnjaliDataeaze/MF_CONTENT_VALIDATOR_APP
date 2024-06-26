import psycopg2
from datetime import datetime
from src.config.queries import INSERT_USER, SELECT_USER
from src.config.credentials import db_config

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()



class User_Manager:

    def login(self, username, password , email):
        try:
            values = (username, password, email)
            cursor.execute(SELECT_USER, values)
            row = cursor.fetchone()
            if row is None:
                return 3
            else:
                saved_password = row[0]
                if saved_password == password:
                    return 1
                else:
                    return 2
        except Exception as error:
            return f"Error : {error}"
    
        

    def add_user(self, username, password,  email, first_name, last_name, phone_number, address):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (username, password, email, first_name, last_name, phone_number, address, now, now)
            cursor.execute(INSERT_USER, values)
            conn.commit()
            return 1
        except Exception as error:
            return f"Error : {error}"
             
    def logout(self):
        pass
        
        
    
