# manager/rules.py
import psycopg2
from src.manager.program import Program
from datetime import datetime
from src.config.queries import INSERT_RULE, SELECT_RULES, UPDATE_RULE, DELETE_RULE, INSERT_RULE_TO_PROGRAM, SELECT_RULES_BY_PROGRAM, PROGRAM_ID, RULE_ID,DELETE_RULE_TO_PROGRAM
from src.config.credentials import db_config


print(db_config)
try:
    print("&&&&&&&&&&&&&&&&&&")
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()

#Rules(rulename, media_type, description, program_type, disclaimer)
class Rules:   
    def __init__(self, rulename, media_type, description, program_type, disclaimer):
        self.rulename = rulename
        self.description = description
        self.disclaimer = disclaimer
        self.media_type = media_type
        self.program_type = program_type

    def add_rule(self):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (self.rulename, self.media_type, self.description, self.disclaimer, now, now)
            cursor.execute(INSERT_RULE, values)

            cursor.execute(PROGRAM_ID, (self.program_type,)) 
            program_id = cursor.fetchone()
            if program_id is None:
                return "No program found"
            cursor.execute(RULE_ID, (self.rulename,))
            rule_id = cursor.fetchone()[0]
            values2 = (program_id, rule_id, now, now)
            cursor.execute(INSERT_RULE_TO_PROGRAM, values2)
            conn.commit()
            return 1
        except Exception as error:
            return f"Error connecting to PostgreSQL: {error}"


        
    @staticmethod
    def list_rules():
        try:
            cursor.execute(SELECT_RULES)
            rules = cursor.fetchall()
            print("List Rules: ", rules)
            return 1, rules
        except Exception as error:
            return 2, f"Error connecting to PostgreSQL: {error}"

    def edit_rule(self, rule_id, new_rulename, new_description, new_disclaimer ):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (new_rulename, new_description, new_disclaimer, now, rule_id)
            print("values",values)
            cursor.execute(UPDATE_RULE, values)
            conn.commit()
            return 1
        except Exception as error:
            return f"Error: {error}"

    def delete_rule(self, rule_id):
        try:
            cursor.execute(DELETE_RULE_TO_PROGRAM,(rule_id,))
            cursor.execute(DELETE_RULE, (rule_id,))

            conn.commit()
            return 1
        except Exception as error:
            return f"Error: {error}"

    def add_rule_to_program(self, rule_id, program_id):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (program_id, rule_id, now, now)
            print("calling add rule to program")
            print(f"values-->{values}")
            cursor.execute(INSERT_RULE_TO_PROGRAM, values)
            conn.commit()
            print("SUccessful")
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