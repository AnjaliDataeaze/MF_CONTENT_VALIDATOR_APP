# manager/rules.py
import psycopg2
from src.manager.program import Program
from datetime import datetime
from src.config.queries import SELECT_MAPPED_RULES, INSERT_RULE, SELECT_RULES, UPDATE_RULE, DELETE_RULE, INSERT_RULE_TO_PROGRAM, SELECT_RULES_BY_PROGRAM, PROGRAM_ID, RULE_ID,DELETE_RULE_TO_PROGRAM
from src.config.credentials import db_config

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()


class Rules:   
    def __init__(self, rulename, media_type, description, disclaimer, assigned_to, ruleStatus, created_by):
        self.rulename = rulename
        self.description = description
        self.disclaimer = disclaimer
        self.media_type = media_type
        self.assigned_to = assigned_to
        self.ruleStatus = ruleStatus
        self.created_by = created_by
    

    @staticmethod
    def add_rule(rulename, media_type, description, disclaimer, assigned_to, ruleStatus, created_by):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (rulename, media_type, description, disclaimer, now, now, assigned_to, ruleStatus, created_by)
            cursor.execute(INSERT_RULE, values)
            conn.commit()
            return {"status": "SUCCESS", "data": "Rule updated successfully !!!"}
        except Exception as error:
            return {"status": "FAILED", "data": f"Error: {error}"}



    @staticmethod
    def edit_rule(rule_id, new_rulename, new_description, new_disclaimer):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (new_rulename, new_description, new_disclaimer, now, rule_id)
            print("values", values)
            cursor.execute(UPDATE_RULE, values)
            conn.commit()
            return {"status": "SUCCESS", "data": "Rule updated successfully !!!"}
        except Exception as error:
            return {"status": "FAILED", "data": f"Error: {error}"}


    @staticmethod
    def delete_rule(rule_id):
        try:
            print("Rule id from frontend:", rule_id)
            cursor.execute(DELETE_RULE_TO_PROGRAM, (rule_id,))
            cursor.execute(DELETE_RULE, (rule_id,))
            conn.commit()
            return {"status": "SUCCESS", "data": "Rule deleted successfully !!!"}
        except Exception as error:
            return {"status": "FAILED", "data": f"Error: {error}"}



    @staticmethod
    def list_rules(status=None):
        try:
            if status:
                query = """
                    SELECT id, rulename, media_type, description, disclaimer, 
                    assigned_to, created_by, rule_status, created_timestamp 
                    FROM rules 
                    WHERE rule_status = %s 
                    ORDER BY id ASC;
                """
                cursor.execute(query, (status,))
            else:
                query = """
                    SELECT id, rulename, media_type, description, disclaimer, 
                    assigned_to, created_by, rule_status, created_timestamp 
                    FROM rules 
                    ORDER BY id ASC;
                """
                cursor.execute(query)
            
            rules = cursor.fetchall()

            # Convert to a list of dictionaries for JSON serialization
            rules_list = [
                {
                    "rule_id": rule[0],
                    "rulename": rule[1],
                    "media_type": rule[2],
                    "description": rule[3],
                    "disclaimer": rule[4],
                    "assigned_to": rule[5],
                    "created_by": rule[6],
                    "rule_status": rule[7],
                    "created_timestamp": rule[8],
                }
                for rule in rules
            ]

            conn.commit()

            return {"status": "SUCCESS", "data": rules_list}
        except Exception as error:
            if conn:
                conn.rollback()
            return {"status": "FAILED", "data": f"Error connecting to PostgreSQL: {error}"}


    @staticmethod
    def filter_rules(term, status=None):
        try:
            if status and status in ['approved', 'pending', 'declined']:
                query = """
                    SELECT id, rulename, media_type, description, disclaimer,
                    assigned_to, created_by, rule_status, created_timestamp
                    FROM rules
                    WHERE (rulename ILIKE %s OR description ILIKE %s) AND rule_status = %s
                    ORDER BY id ASC;
                """
                cursor.execute(query, (f'%{term}%', f'%{term}%', status))
            else:
                query = """
                    SELECT id, rulename, media_type, description, disclaimer,
                    assigned_to, created_by, rule_status, created_timestamp
                    FROM rules
                    WHERE rulename ILIKE %s OR description ILIKE %s
                    ORDER BY id ASC;
                """
                cursor.execute(query, (f'%{term}%', f'%{term}%'))
            rules = cursor.fetchall()
            rules_list = [
                {
                    "rule_id": rule[0],
                    "rulename": rule[1],
                    "media_type": rule[2],
                    "description": rule[3],
                    "disclaimer": rule[4],
                    "assigned_to": rule[5],
                    "created_by": rule[6],
                    "rule_status": rule[7],
                    "created_timestamp": rule[8]
                }
                for rule in rules
            ]
            return {"status": "SUCCESS", "data": rules_list}
        except Exception as error:
            return {"status": "FAILED", "data": f"Error connecting to PostgreSQL: {error}"}



    @staticmethod
    def get_mapped_rules(program_id):
        try:
            cursor.execute(SELECT_MAPPED_RULES, (program_id,))
            rules = cursor.fetchall()
            
            # Convert the result to a list of dictionaries
            rules_list = [
                {
                    "rule_id": rule[0],
                    "rulename": rule[1],
                    "media_type": rule[2],
                    "disclaimer": rule[3]
                }
                for rule in rules
            ]
            conn.commit()
            return {"status": "SUCCESS", "data": rules_list}
        except Exception as error:
            if conn:
                conn.rollback()
            return {"status": "FAILED", "data": f"Error: {error}"}

    @staticmethod
    def change_rule_status(rule_id, status):
        try:
            cursor.execute("UPDATE rules SET rule_status = %s WHERE rule_id = %s", (status, rule_id))
            conn.commit()
            return {"status": "SUCCESS", "data": "Rule status updated successfully !!!"}
        except Exception as error:
            if conn:
                conn.rollback()
            return {"status": "FAILED", "data": f"Error connecting to PostgreSQL: {error}"}