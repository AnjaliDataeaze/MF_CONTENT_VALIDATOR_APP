import psycopg2
from datetime import datetime
from src.config.queries import INSERT_USER, SELECT_PASSWORD, LIST_USER, UPDATE_USER, DELETE_USER
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
            if conn:
                conn.rollback()
            return f"Error connecting to PostgreSQL: {error}"
        # finally:
        #     if cursor:
        #         cursor.close()
        #     if conn:
        #         conn.close()
            
        

    def add_user(self, email, password, first_name, last_name, phone_number, role, status):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (email, password, first_name, last_name, phone_number, role, status, now, now)
            cursor.execute(INSERT_USER, values)
            conn.commit()
            return 1
        except Exception as error:
            if conn:
                conn.rollback()
            return f"Error connecting to PostgreSQL: {error}"
            #return {"status": "FAILED", "message": f"Error connecting to PostgreSQL: {error}"}
        # finally:
        #     if cursor:
        #         cursor.close()
        #     if conn:
        #         conn.close()
    


    def list_user(self):
        try:
            print("Calling list of user")
            cursor.execute(LIST_USER)
            row = cursor.fetchall()
            print("Row", row)
            return 1, row 
        except Exception as error:
            if conn:
                conn.rollback()
            return 2, f"Error connecting to PostgreSQL: {error}"
        # finally:
        #     if cursor:
        #         cursor.close()
        #     if conn:
        #         conn.close()


    def filter_user(self, search):
        try:
            FILTER_USER = """
            SELECT user_id, first_name, last_name, email, phone_number, role, status
            FROM users
            WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s OR role ILIKE %s;
            """

            search_term = f"%{search}%"
            cursor.execute(FILTER_USER, (search_term, search_term, search_term, search_term))
            row = cursor.fetchall()
            return {"status": "SUCCESS", "data": row}
        except Exception as error:
            if conn:
                conn.rollback()
            return {"status": "FAILED", "message": f"Error connecting to PostgreSQL: {error}"}







    def edit_user(self, first_name, last_name, email, phone_number, role, status):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (first_name, last_name, phone_number, role, status, now, email)
            print("Valuess-->", values)
            cursor.execute(UPDATE_USER, values)
            conn.commit()
            return 1 
        except Exception as error:
            if conn:
                conn.rollback()
            return f"Error connecting to PostgreSQL: {error}"
        # finally:
        #     if cursor:
        #         cursor.close()
        #     if conn:
        #         conn.close()
        
        

    def delete_user(self, user_id):
        try:
            
            cursor.execute(DELETE_USER,(user_id,))
            conn.commit()
            return 1
        except Exception as error:
            if conn:
                conn.rollback()
            return f"Error connecting to PostgreSQL: {error}"
        # finally:
        #     if cursor:
        #         cursor.close()
        #     if conn:
        #         conn.close()


    
   
        
    