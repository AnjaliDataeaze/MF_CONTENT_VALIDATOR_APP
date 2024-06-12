# manager/config/queries.py

INSERT_PROGRAM = """
    INSERT INTO program (name, description, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s)
"""

SELECT_PROGRAMS = "SELECT name, description, id FROM program order by id ASC ;"

UPDATE_PROGRAM = """
    UPDATE program
    SET name = %s, description = %s, lastupdated_timestamp = %s
    WHERE id = %s
"""

DELETE_PROGRAM = "DELETE FROM program WHERE id = %s"
RULE_ID_RULE_TO_PROGRAM = "SELECT rules_id FROM rule_to_program WHERE program_id = %s"

DELETE_RULENAMES = "DELETE FROM rules WHERE id in %s"

INSERT_RULE = """
    INSERT INTO rules (rulename, media_type, description, disclaimer, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s, %s, %s)
"""

SELECT_RULES = "SELECT r.rulename, r.media_type, r.description, r.disclaimer, p.name as program_type, r.id FROM rules as r join rule_to_program rp on r.id = rp.rules_id join program p on rp.program_id = p.id ;"

UPDATE_RULE = """
    UPDATE rules 
    SET rulename = %s, description = %s, disclaimer = %s, lastupdated_timestamp = %s 
    WHERE id = %s
"""
PROGRAM_ID = """
    SELECT id FROM program WHERE name = %s
"""
RULE_ID = """
    SELECT id FROM rules WHERE rulename = %s
"""

DELETE_RULE_TO_PROGRAM = "DELETE FROM rule_to_program WHERE rules_id = %s"
DELETE_RULE = "DELETE FROM rules WHERE id = %s"

DELETE_PROGRAM_TO_RULE = "DELETE FROM rule_to_program WHERE rules_id = %s"
DELETE_RULENAMES_2 = "DELETE FROM rules WHERE id in %s"
DELETE_RULENAMES_1 = "DELETE FROM rules WHERE id = %s"


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

# Queries for validation-----------
GET_PROGRAM_ID = """
                SELECT id FROM program WHERE name = %s
                """

GET_Rule_ID_ASSOCIATED_WITH_PROGRAM = """
                SELECT rules_id FROM rule_to_program WHERE program_id = %s
                """

GET_DECRIPTION_FOR_RULE_ID = """
                    SELECT id, disclaimer FROM rules WHERE id = %s
                    """