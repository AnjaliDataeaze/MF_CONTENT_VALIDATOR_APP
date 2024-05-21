# manager/config/queries.py

INSERT_PROGRAM = """
    INSERT INTO Program (name, description, Creation_timestamp, Updation_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_PROGRAMS = "SELECT * FROM Program"

UPDATE_PROGRAM = """
    UPDATE Program 
    SET name = %s, description = %s, Updation_timestamp = %s 
    WHERE id = %s
"""

DELETE_PROGRAM = "DELETE FROM Program WHERE id = %s"

INSERT_RULE = """
    INSERT INTO Rules (rulename, media_type, description, Creation_timestamp, Updation_timestamp) 
    VALUES (%s, %s, %s, %s, %s)
"""

SELECT_RULES = "SELECT * FROM Rules"

UPDATE_RULE = """
    UPDATE Rules 
    SET rulename = %s, media_type = %s, description = %s, Updation_timestamp = %s 
    WHERE id = %s
"""

DELETE_RULE = "DELETE FROM Rules WHERE id = %s"

INSERT_DISCLAIMER = """
    INSERT INTO Disclaimer (rule_id, disclaimer, Creation_timestamp, Updation_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_DISCLAIMERS = "SELECT * FROM Disclaimer"

UPDATE_DISCLAIMER = """
    UPDATE Disclaimer 
    SET rule_id = %s, disclaimer = %s, Updation_timestamp = %s 
    WHERE id = %s
"""

DELETE_DISCLAIMER = "DELETE FROM Disclaimer WHERE id = %s"

INSERT_RULE_TO_PROGRAM = """
    INSERT INTO Rule_to_program (program_id, rules_id, Creation_timestamp, Updation_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_RULES_BY_PROGRAM = """
    SELECT r.* FROM Rules r
    JOIN Rule_to_program rp ON r.id = rp.rules_id
    WHERE rp.program_id = %s
"""

INSERT_DOCUMENT = """
    INSERT INTO Document (doc_name, doc_type, Creation_timestamp, Updation_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_DOCUMENTS = "SELECT * FROM Document"

UPDATE_DOCUMENT = """
    UPDATE Document 
    SET doc_name = %s, doc_type = %s, Updation_timestamp = %s 
    WHERE doc_id = %s
"""

DELETE_DOCUMENT = "DELETE FROM Document WHERE doc_id = %s"

INSERT_DOCUMENT_TO_PROGRAM = """
    INSERT INTO Document_to_program (doc_id, program_id, Creation_timestamp, Updation_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_DOCUMENTS_BY_PROGRAM = """
    SELECT d.* FROM Document d
    JOIN Document_to_program dp ON d.doc_id = dp.doc_id
    WHERE dp.program_id = %s
"""
