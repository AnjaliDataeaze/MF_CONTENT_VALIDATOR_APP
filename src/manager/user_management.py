import psycopg2
from datetime import datetime
from src.config.queries import INSERT_USER, SELECT_PASSWORD, LIST_USER
from src.config.credentials import db_config

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()



class User_Manager:

    def login(self, email, password):
        try:
            values = (email)
            query = f"SELECT password FROM users WHERE email='{email}'"
            cursor.execute(query)
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
    
        

    def add_user(self, username, password, email, first_name, last_name, phone_number):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (username, password, email, first_name, last_name, phone_number, now, now)
            cursor.execute(INSERT_USER, values)
            conn.commit()
            return 1
        except Exception as error:
            return 2, f"Error : {error}"
             

    def list_user(self):
        try:
            cursor.execute(LIST_USER)
            row= cursor.fetchall()
            print("LIST_USER")
            print(row)
            return 1, row 
        except Exception as e:
            return 2 , str(e)


    def logout(self):
        pass
        
        
    
