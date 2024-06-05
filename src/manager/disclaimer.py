# manager/disclaimer.py
import psycopg2
from src.manager.rules import Rules
from datetime import datetime
from src.config.queries import INSERT_DISCLAIMER, SELECT_DISCLAIMERS, UPDATE_DISCLAIMER, DELETE_DISCLAIMER
from src.config.credentials import db_config

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
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
            conn.commit()
            # return "Disclaimer added successfully!"
            return 1
        except Exception as error:
            return f"Error : {error}"

    @staticmethod
    def list_disclaimers():
        try:
            cursor.execute(SELECT_DISCLAIMERS)
            disclaimers = cursor.fetchall()
            return 1, disclaimers
        except Exception as error:
            return 2,f"Error : {error}"

    def edit_disclaimer(self, disclaimer_id, new_rule_id, new_actual_disclaimer):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (new_rule_id, new_actual_disclaimer, now, disclaimer_id)
            cursor.execute(UPDATE_DISCLAIMER, values)
            conn.commit()
            # return "Disclaimer updated successfully!"
            return 1
        except Exception as error:
            return f"Error : {error}"

    def delete_disclaimer(self, disclaimer_id):
        try:
            cursor.execute(DELETE_DISCLAIMER, (disclaimer_id,))
            conn.commit()
            # return "Disclaimer deleted successfully!"
            return 1
        except Exception as error:
            return f"Error : {error}"
