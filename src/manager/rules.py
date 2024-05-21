# manager/rules.py

import mysql.connector
from manager.program import Program
from datetime import datetime
from src.config.queries import INSERT_RULE, SELECT_RULES, UPDATE_RULE, DELETE_RULE, INSERT_RULE_TO_PROGRAM, SELECT_RULES_BY_PROGRAM
from src.config.credentials import db_config

try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit()

class Rules(Program):
    def __init__(self, rulename, media_type, description, program_id=None):
        self.rulename = rulename
        self.media_type = media_type
        self.description = description
        self.program_id = program_id

    def add_rule(self):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (self.rulename, self.media_type, self.description, now, now)
            cursor.execute(INSERT_RULE, values)
            rule_id = cursor.lastrowid
            db.commit()
            if self.program_id:
                self.add_rule_to_program(rule_id, self.program_id)
            return "Rule added successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

    @staticmethod
    def list_rules():
        try:
            cursor.execute(SELECT_RULES)
            rules = cursor.fetchall()
            return rules
        except mysql.connector.Error as err:
            return f"Error: {err}"

    def edit_rule(self, rule_id, new_rulename, new_media_type, new_description):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (new_rulename, new_media_type, new_description, now, rule_id)
            cursor.execute(UPDATE_RULE, values)
            db.commit()
            return "Rule updated successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

    def delete_rule(self, rule_id):
        try:
            cursor.execute(DELETE_RULE, (rule_id,))
            db.commit()
            return "Rule deleted successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

    def add_rule_to_program(self, rule_id, program_id):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (program_id, rule_id, now, now)
            cursor.execute(INSERT_RULE_TO_PROGRAM, values)
            db.commit()
            return "Rule linked to program successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

    @staticmethod
    def list_rules_by_program(program_id):
        try:
            cursor.execute(SELECT_RULES_BY_PROGRAM, (program_id,))
            rules = cursor.fetchall()
            return rules
        except mysql.connector.Error as err:
            return f"Error: {err}"
