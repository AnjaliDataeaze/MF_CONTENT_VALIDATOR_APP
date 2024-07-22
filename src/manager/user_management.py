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
            query = f"SELECT password, user_id, first_name, last_name, email, phone_number, status, role FROM users WHERE email='{email}'"
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return 3
            else:
                saved_password = row[0]
                if saved_password == password:
                    details =[]
                    for i in range(1, len(row)):
                        details.append(row[i])
                    return 1 , details
                else:
                    return 2 , details
                
        except Exception as error:
            if conn:
                conn.rollback()
            return f"Error connecting to PostgreSQL: {error}"


    @staticmethod
    def add_user(email, password, first_name, last_name, phone_number, role, status):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (email, password, first_name, last_name, phone_number, role, status, now, now)
            cursor.execute(INSERT_USER, values)
            conn.commit()

            response = {"status": "SUCCESS", "data": "User added successfully!"}
       
        except Exception as error:
            if conn:
                conn.rollback()
           
            response = {"status": "FAILED", "data": f"Error connecting to PostgreSQL: {error}"}
        
        return response



    def list_users(self):
        try:
            cursor.execute(LIST_USER)
            rows = cursor.fetchall()

            # Process fetched user records into the desired JSON format
            fetched_users = [
                {
                    "userID": row[0],
                    "firstName": row[1],
                    "lastName": row[2],
                    "email": row[3],
                    "phoneNumber": row[4],
                    "role": row[5],
                    "status": row[6]
                }
                for row in rows
            ]

            response = {
                "body": {
                    "status": "SUCCESS",
                    "data": fetched_users,
                    "total_count": len(fetched_users)
                },
                "statusCode": 200
            }
            return response

        except Exception as error:
            if conn:
                conn.rollback()
            return {"body": {"status": "FAILED", "data": f"Error connecting to PostgreSQL: {error}"}, "statusCode": 500}


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

            # Process fetched user records
            fetched_users = [
                {
                    "userID": user[0],
                    "firstName": user[1],
                    "lastName": user[2],
                    "email": user[3],
                    "phoneNumber": user[4],
                    "role": user[5],
                    "status": user[6]
                }
                for user in row
            ]

            # Construct the response format
            response = {
                "body": {
                    "status": "SUCCESS",
                    "data": fetched_users,
                    "total_count": len(fetched_users)
                },
                "statusCode": 200
            }
            return response

        except Exception as error:
            if conn:
                conn.rollback()
            return {"body": {"status": "FAILED", "message": f"Error connecting to PostgreSQL: {error}"}, "statusCode": 500}


                    # return {"status": "FAILED", "message": f"Error connecting to PostgreSQL: {error}"}

    def edit_user(self, first_name, last_name, email, phone_number, role, status):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (first_name, last_name, phone_number, role, status, now, email)
            print("Values -->", values)
            cursor.execute(UPDATE_USER, values)
            conn.commit()
            return {"status": "SUCCESS", "data": "User updated successfully !!!"}
        except Exception as error:
            if conn:
                conn.rollback()
            return {"status": "FAILED", "data": f"Error connecting to PostgreSQL: {error}"}

    
   
        
    def delete_user(self, user_id):
        try:
            cursor.execute(DELETE_USER, (user_id,))
            conn.commit()
            return {"status": "SUCCESS", "data": "User deleted successfully"}
        except Exception as error:
            if conn:
                conn.rollback()
            return {"status": "FAILED", "data": f"Error connecting to PostgreSQL: {error}"}

