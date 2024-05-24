# manager/config/queries.py

INSERT_PROGRAM = """
    INSERT INTO program (name, description, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_PROGRAMS = "SELECT * FROM program"

UPDATE_PROGRAM = """
    UPDATE program 
    SET name = %s, description = %s, lastupdated_timestamp = %s 
    WHERE id = %s
"""

DELETE_PROGRAM = "DELETE FROM program WHERE id = %s"

INSERT_RULE = """
    INSERT INTO rules (rulename, media_type, description, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s, %s)
"""

SELECT_RULES = "SELECT * FROM rules"

UPDATE_RULE = """
    UPDATE rules 
    SET rulename = %s, media_type = %s, description = %s, lastupdated_timestamp = %s 
    WHERE id = %s
"""

DELETE_RULE = "DELETE FROM rules WHERE id = %s"

INSERT_DISCLAIMER = """
    INSERT INTO disclaimer (rule_id, disclaimer, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_DISCLAIMERS = "SELECT * FROM disclaimer"

UPDATE_DISCLAIMER = """
    UPDATE disclaimer 
    SET rule_id = %s, disclaimer = %s, lastupdated_timestamp = %s 
    WHERE id = %s
"""

DELETE_DISCLAIMER = "DELETE FROM disclaimer WHERE id = %s"

INSERT_RULE_TO_PROGRAM = """
    INSERT INTO rule_to_program (program_id, rules_id, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_RULES_BY_PROGRAM = """
    SELECT r.* FROM rules r
    JOIN rule_to_program rp ON r.id = rp.rules_id
    WHERE rp.program_id = %s
"""

INSERT_DOCUMENT = """
    INSERT INTO document (doc_name, doc_type, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_DOCUMENTS = "SELECT * FROM document"

UPDATE_DOCUMENT = """
    UPDATE document 
    SET doc_name = %s, doc_type = %s, lastupdated_timestamp = %s 
    WHERE doc_id = %s
"""

DELETE_DOCUMENT = "DELETE FROM document WHERE doc_id = %s"

INSERT_DOCUMENT_TO_PROGRAM = """
    INSERT INTO document_to_program (doc_id, program_id, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_DOCUMENTS_BY_PROGRAM = """
    SELECT d.* FROM document d
    JOIN document_to_program dp ON d.doc_id = dp.doc_id
    WHERE dp.program_id = %s
"""
