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
        self.created_by = created_by
    
    @staticmethod
    def add_program(name, description, rules, created_by):
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = (name, description,created_by, now, now)
            cursor.execute(INSERT_PROGRAM, values)
            print("Insert program done")

            cursor.execute(PROGRAM_ID, (name,)) 
            program_id = cursor.fetchone()
            print("Program Id: ",program_id)
            for rule_name in rules:
                cursor.execute("SELECT id FROM rules WHERE rulename = %s", (rule_name,))
                rule_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO rule_to_program (program_id, rules_id) VALUES (%s, %s)", (program_id, rule_id))
            print("Rules are mapped with ")

            conn.commit()
            return {"status": "SUCCESS", "data": "Program added successfully !!!"}
        except Exception as error:
            return {"status": "FAILED", "data": f"Error: {error}"}



    @staticmethod
    def list_programs():
        try:
            cursor.execute(SELECT_PROGRAMS)
            programs = cursor.fetchall()

            # Process fetched program records into the desired JSON format
            fetched_programs = [
                {
                    "programID": program[2],
                    "programName": program[0],
                    "description": program[1],
                    "created_by": program[3],
                    "created_at": program[4]
                }
                for program in programs
            ]

            response = {
                "body": {
                    "status": "success",
                    "data": fetched_programs,
                    "total_count": len(fetched_programs)
                },
                "statusCode": 200
            }
            return response
        
        except Exception as error:
            return {"body": {"status": "failed", "data": str(error)}, "statusCode": 500}


    @staticmethod
    def edit_program( program_id, name, description, rules):
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
            return {"status": "SUCCESS", "data": "Program updated successfully !!!"}
            #return 1;
        except Exception as error:
            return {"status": "FAILED", "data": f"Error: {error}"}


    @staticmethod
    def delete_program(program_id):
        try:
            cursor.execute(DELETE_RULE_TO_PROGRAM_FROM_PROGRAM, (program_id,)) # delete from rulr_to_program
            cursor.execute(DELETE_PROGRAM, (program_id,)) # delete from program
            conn.commit()
            return {"status": "SUCCESS", "data": "Program deleted successfully !!!"}
        except Exception as error:
            if conn:
                conn.rollback()
            return {"status": "FAILED", "data": f"Error: {error}"}