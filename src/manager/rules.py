# manager/rules.py
import psycopg2
from src.manager.program import Program
from datetime import datetime
from src.config.queries import INSERT_RULE, SELECT_RULES, UPDATE_RULE, DELETE_RULE, INSERT_RULE_TO_PROGRAM, SELECT_RULES_BY_PROGRAM
from src.config.credentials import db_config

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()


# class Rules(Program):
class Rules:
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
            conn.commit()
            if self.program_id:
                cursor.execute(f"select id from rules where rulename = '{self.rulename}' and media_type='{self.media_type}' and created_timestamp='{now}'")
                row = cursor.fetchone()
                print(row)
                rule_id = row[0]
                val = self.add_rule_to_program(rule_id, self.program_id)
                if val ==1:
                    return 1
                else:
                    return val
        except Exception as error:
            return f"Error connecting to PostgreSQL: {error}"

    @staticmethod
    def list_rules():
        try:
            cursor.execute(SELECT_RULES)
            rules = cursor.fetchall()
            return 1, rules
        except Exception as error:
            return 2, f"Error connecting to PostgreSQL: {error}"

    def edit_rule(self, rule_id, new_rulename, new_media_type, new_description):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (new_rulename, new_media_type, new_description, now, rule_id)
            cursor.execute(UPDATE_RULE, values)
            conn.commit()
            # return "Rule updated successfully!"
            return 1
        except Exception as error:
            return f"Error : {error}"

    def delete_rule(self, rule_id):
        try:
            cursor.execute(DELETE_RULE, (rule_id,))
            conn.commit()
            # return "Rule deleted successfully!"
            return 1
        except Exception as error:
            return f"Error : {error}"

    def add_rule_to_program(self, rule_id, program_id):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (program_id, rule_id, now, now)
            cursor.execute(INSERT_RULE_TO_PROGRAM, values)
            conn.commit()
            # return "Rule linked to program successfully!"
            return 1
        except Exception as error:
            return f"Error : {error}"

    @staticmethod
    def list_rules_by_program(program_id):
        try:
            cursor.execute(SELECT_RULES_BY_PROGRAM, (program_id,))
            rules = cursor.fetchall()
            return 1, rules
        except Exception as error:
            return 2,f"Error : {error}"

    if cursor:
        cursor.close()
    if conn:
        conn.close()