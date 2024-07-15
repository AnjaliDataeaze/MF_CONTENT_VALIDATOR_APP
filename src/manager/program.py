# manager/main.py

import psycopg2
from datetime import datetime
from src.config.queries import DELETE_RULE_TO_PROGRAM_FROM_PROGRAM, PROGRAM_ID,INSERT_PROGRAM, SELECT_PROGRAMS, UPDATE_PROGRAM, DELETE_PROGRAM, RULE_ID_RULE_TO_PROGRAM, DELETE_PROGRAM_TO_RULE,DELETE_RULENAMES_1
from src.config.credentials import db_config
from fastapi import APIRouter, HTTPException

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()


class Program:
    def __init__(self, name, description, rules):
        self.name = name
        self.description = description
        self.rules = rules
    def add_program(self):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (self.name, self.description, now, now)
            print("Value : ",values)
            print("Insert program",INSERT_PROGRAM)
            cursor.execute(INSERT_PROGRAM, values)
            
            print("Insert program done")
            print("--------",PROGRAM_ID)
            name = self.name
            print("---sssss---",name)
            cursor.execute(PROGRAM_ID, (self.name,)) 
            program_id = cursor.fetchone()
            print("Program Id: ",program_id)
            for rule_name in self.rules:
                print(rule_name)
                print(self.rules)
                cursor.execute("SELECT id FROM rules WHERE rulename = %s", (rule_name,))
                rule_id = cursor.fetchone()[0]
                print("Rule Id",rule_id)
                cursor.execute("INSERT INTO rule_to_program (program_id, rules_id) VALUES (%s, %s)", (program_id, rule_id))
                print("Finallll")

            conn.commit()
            return 1
        except Exception as error:
            return f"Error : {error}"

    @staticmethod
    def list_programs():
        try:
            # print("SELECT_PROGRAMS",SELECT_PROGRAMS)
            cursor.execute(SELECT_PROGRAMS)
        
            programs = cursor.fetchall()
            # print("the fetched Data is: ",programs)
            return 1, programs
        except Exception as error:
            return 2, f"Error: {error}" 

    def edit_program(self, program_id, name, description, rules):
        '''try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (name, description, now, program_id)
            print("Passed Values: ",values)
            cursor.execute(UPDATE_PROGRAM, values)
            conn.commit()
            return 1
        except Exception as error:
            return f"Error : {error}"
        '''
        try:
            print("Inside manager program")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Update the program details
            update_program_query = """
                UPDATE program
                SET name = %s, description = %s, lastupdated_timestamp = %s
                WHERE id = %s """
            print("update_program_query", update_program_query)
            print("name, dec, time, id ",name,description, now,program_id)
            cursor.execute(update_program_query, (name,description,now,program_id))

            # Delete existing rules for the program
            delete_rules_query = "DELETE FROM rule_to_program WHERE program_id = %s"
            cursor.execute(delete_rules_query, (program_id,))
            print("delete_rules_query",delete_rules_query)
            
             # Insert new rules for the program
            insert_rule_query = "INSERT INTO rule_to_program (program_id, rules_id) VALUES (%s, %s)"
            print("insert_rule_query",insert_rule_query)

            for rule_name in rules:
                cursor.execute("SELECT id FROM rules WHERE rulename = %s", (rule_name,))
                rule_id = cursor.fetchone()
                if rule_id:
                    cursor.execute(insert_rule_query, (program_id, rule_id[0]))

            conn.commit()
            #return {"status": "SUCCESS", "data": "Program updated successfully !!!"}
            return 1;
        except Exception as error:
            return f"Error : {error}"
            #if conn:
             #   conn.rollback()
            #raise HTTPException(status_code=500, detail=str(error))

    def delete_program(self, program_id):
        try:
            cursor.execute(DELETE_RULE_TO_PROGRAM_FROM_PROGRAM,(program_id,)) # delete from rulr_to_program
            cursor.execute(DELETE_PROGRAM, (program_id,)) # delete from program
            conn.commit()
            return 1
        except Exception as error:
            return f"Error: {error}"

        """
        try:
            cursor.execute(RULE_ID_RULE_TO_PROGRAM,(program_id,)) #fetch ruleids from rule_to_program
            rule_ids = tuple(cursor.fetchall())
            if rule_ids:
                rule_ids_flat = tuple(rule_id[0] for rule_id in rule_ids)
                cursor.execute(DELETE_PROGRAM_TO_RULE,(rule_ids_flat)) # delete from rulr_to_program
                #cursor.execute(DELETE_RULENAMES_1,(rule_ids_flat)) #delete from rules 
                 #delete from rule_to_program
            
            cursor.execute(DELETE_PROGRAM, (program_id,)) # delete from program
            
            conn.commit()
            return 1
        except Exception as error:
            return f"Error : {error}" 
        """