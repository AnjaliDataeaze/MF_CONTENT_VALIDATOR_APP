INSERT_PROGRAM = """
    INSERT INTO program (name, description,created_by, created_timestamp, lastupdated_timestamp) 
    VALUES (%s, %s, %s, %s, %s)
"""

SELECT_PROGRAMS = "SELECT name, description, id, created_by, created_timestamp FROM program order by id ASC ;"
UPDATE_PROGRAM = """
    UPDATE program
    SET name = %s, description = %s, lastupdated_timestamp = %s
    WHERE id = %s
"""

DELETE_PROGRAM = "DELETE FROM program WHERE id = %s"
DELETE_RULE_TO_PROGRAM_FROM_PROGRAM = "DELETE FROM rule_to_program WHERE program_id = %s"
RULE_ID_RULE_TO_PROGRAM = "SELECT rules_id FROM rule_to_program WHERE program_id = %s"

DELETE_RULENAMES = "DELETE FROM rules WHERE id in %s"

INSERT_RULE = """
    INSERT INTO rules (rulename, media_type, description, disclaimer, created_timestamp, lastupdated_timestamp, assigned_to, rule_status, created_by) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

SELECT_RULES = "SELECT id, rulename, media_type, description, disclaimer FROM rules;"

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

SELECT_MAPPED_RULES = """
    SELECT r.id, r.rulename, r.media_type, r.disclaimer
    FROM rules r
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
                    SELECT rulename, disclaimer FROM rules WHERE id = %s
                    """

RETURN_OUTPUT = """
                        SELECT rulename, rule, answer, output
                        FROM output
                        WHERE group_id = %s
                        """

CREATE_SEQUENCE_GROUP_ID = """
                        CREATE SEQUENCE IF NOT EXISTS group_id_seq
                        START 1;
                    """

NEXTVAL_GROUP_ID = "SELECT nextval('group_id_seq')"




INSERT_RESULTS = """ INSERT INTO results (video_link, media_type, timestamp)
                    VALUES (%s, %s, %s) RETURNING parent_id
                    """
INSERT_OUTPUT_RESULTS = """INSERT INTO output_results (parent_id, group_id, document_link, rule_id, rule, rulename, answer, output, time_stamp)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """
INSERT_OUTPUT = ""
## Queries for User Managememnt


INSERT_USER = """ INSERT INTO users (email, password, first_name, last_name, phone_number, role, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
SELECT_PASSWORD = """SELECT password FROM users WHERE email= %s """

LIST_USER = "SELECT  user_id, first_name, last_name, email, phone_number, role, status  FROM users "

UPDATE_USER = """ UPDATE users SET
                  first_name = %s,
                  last_name = %s, 
                  phone_number= %s,
                  role = %s,
                  status = %s,
                  updated_at = %s 
                  WHERE email = %s"""


DELETE_USER = """ DELETE FROM users WHERE user_id = %s"""

SELECT_RULES_BY_PROGRAM_VIDEO = """
    SELECT r.id, r.rulename, r.disclaimer
    FROM rules r
    JOIN rule_to_program rp ON r.id = rp.rules_id
    WHERE rp.program_id = %s AND (r.media_type = 'Video' OR r.media_type = 'PDF/Image')
"""

SELECT_RULES_BY_PROGRAM_AUDIO = """
    SELECT r.id, r.rulename, r.disclaimer
    FROM rules r
    JOIN rule_to_program rp ON r.id = rp.rules_id
    WHERE rp.program_id = %s AND r.media_type = 'audio' """

#------------ Queries For Source Metadata-----------------------------#

INSERT_MASTER_QUERY = """
                INSERT INTO Ref_dset_master (dset_name, description, lookup_key_colname, all_col_names)
                VALUES (%s, %s, %s, %s) RETURNING Id;
                """

INSERT_RECORD_QUERY = """
                INSERT INTO Ref_dset_records (type_id, col_name, col_value, lk_colname, lk_colvalue)
                VALUES %s;
                """
LIST_DATASET = """SELECT dset_name from  ref_dset_master;"""


LIST_DATASET_INFO = """ SELECT id ,dset_name, description, all_col_names FROM ref_dset_master;
"""

LIST_DATASET_RECORDS =  """
SELECT  col_name, col_value, lk_colname, lk_colvalue
FROM ref_dset_records where type_id = %s
"""


LIST_SCHEME = """
                SELECT DISTINCT r.lk_colvalue
                FROM ref_dset_master m
                JOIN ref_dset_records r ON m.id = r.type_id
                WHERE m.dset_name = %s;
"""


