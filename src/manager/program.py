# manager/main.py

import psycopg2
from datetime import datetime
from src.config.queries import INSERT_PROGRAM, SELECT_PROGRAMS, UPDATE_PROGRAM, DELETE_PROGRAM
from src.config.credentials import db_config

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()


class Program:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def add_program(self):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (self.name, self.description, now, now)
            cursor.execute(INSERT_PROGRAM, values)
            conn.commit()
            return 1
            # return "Program added successfully!"
        except Exception as error:
            return f"Error : {error}"

    @staticmethod
    def list_programs():
        try:
            cursor.execute(SELECT_PROGRAMS)
            programs = cursor.fetchall()
            return 1, programs
        except Exception as error:
            return 2,f"Error : {error}"

    def edit_program(self, program_id, new_name, new_description):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (new_name, new_description, now, program_id)
            cursor.execute(UPDATE_PROGRAM, values)
            conn.commit()
            # return "Program updated successfully!"
            return 1
        except Exception as error:
            return 2,f"Error : {error}"

    def delete_program(self, program_id):
        try:
            cursor.execute(DELETE_PROGRAM, (program_id,))
            conn.commit()
            # return "Program deleted successfully!"
            return 1
        except Exception as error:
            return 2,f"Error : {error}"




