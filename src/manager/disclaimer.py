# manager/disclaimer.py

import mysql.connector
from src.manager.rules import Rules
from datetime import datetime
from src.config.queries import INSERT_DISCLAIMER, SELECT_DISCLAIMERS, UPDATE_DISCLAIMER, DELETE_DISCLAIMER
from src.config.credentials import db_config

try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit()

class Disclaimer(Rules):
    def __init__(self, name_of_disclaimer, rule_id, actual_disclaimer):
        self.name_of_disclaimer = name_of_disclaimer
        self.rule_id = rule_id
        self.actual_disclaimer = actual_disclaimer

    def add_disclaimer(self):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (self.rule_id, self.actual_disclaimer, now, now)
            cursor.execute(INSERT_DISCLAIMER, values)
            db.commit()
            return "Disclaimer added successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

    @staticmethod
    def list_disclaimers():
        try:
            cursor.execute(SELECT_DISCLAIMERS)
            disclaimers = cursor.fetchall()
            return disclaimers
        except mysql.connector.Error as err:
            return f"Error: {err}"

    def edit_disclaimer(self, disclaimer_id, new_rule_id, new_actual_disclaimer):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (new_rule_id, new_actual_disclaimer, now, disclaimer_id)
            cursor.execute(UPDATE_DISCLAIMER, values)
            db.commit()
            return "Disclaimer updated successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

    def delete_disclaimer(self, disclaimer_id):
        try:
            cursor.execute(DELETE_DISCLAIMER, (disclaimer_id,))
            db.commit()
            return "Disclaimer deleted successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

