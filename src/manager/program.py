# manager/main.py

import mysql.connector
from datetime import datetime
from src.config.queries import INSERT_PROGRAM, SELECT_PROGRAMS, UPDATE_PROGRAM, DELETE_PROGRAM
from src.config.credentials import db_config

try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
except mysql.connector.Error as err:
        print(f"Error: {err}")
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
            db.commit()
            return "Program added successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

    @staticmethod
    def list_programs():
        try:
            cursor.execute(SELECT_PROGRAMS)
            programs = cursor.fetchall()
            return programs
        except mysql.connector.Error as err:
            return f"Error: {err}"

    def edit_program(self, program_id, new_name, new_description):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (new_name, new_description, now, program_id)
            cursor.execute(UPDATE_PROGRAM, values)
            db.commit()
            return "Program updated successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

    def delete_program(self, program_id):
        try:
            cursor.execute(DELETE_PROGRAM, (program_id,))
            db.commit()
            return "Program deleted successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"




