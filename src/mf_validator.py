# mf_validator.py


from src.manager.program import Program
from src.manager.rules import Rules
from src.manager.disclaimer import Disclaimer
from src.manager.validation import AnalyzeDocument
from src.config.prompts import PROMPT
from src.manager.transcription import Final
# class validator:
def add_program(name, description):
    program = Program(name, description)
    return program.add_program()

def list_programs():
    return Program.list_programs()

def edit_program(program_id, name, description):
    program = Program("", "")
    return program.edit_program(program_id, name, description)


def delete_program(program_id):
    program = Program("", "")
    return program.delete_program(program_id)

# ------------------------------------------------------------#


def add_rule(rulename, media_type, description, program_type, disclaimer):
    rule = Rules(rulename, media_type, description, program_type, disclaimer)
    return rule.add_rule()

def list_rules():
    return Rules.list_rules()

def edit_rule(rulename, description, disclaimer, rule_id):
    rule = Rules("", "", "", "", "")
    return rule.edit_rule(rulename, description, disclaimer, rule_id)

def delete_rule(rule_id):
    rule = Rules("","", "", "", "")
    return rule.delete_rule(rule_id)

def list_rules_by_program(program_id):
    return Rules.list_rules_by_program(program_id)

# ------------------------------------------------------------#

def add_disclaimer(rule_id, actual_disclaimer):    
    disclaimer = Disclaimer()
    return disclaimer.add_disclaimer(rule_id, actual_disclaimer)

def list_disclaimers():
    disclaimer = Disclaimer()
    return disclaimer.list_disclaimers()

def edit_disclaimer(disclaimer_id, rule_id, actual_disclaimer):
    disclaimer = Disclaimer()
    return disclaimer(disclaimer_id, rule_id, actual_disclaimer)

def delete_disclaimer(disclaimer_id):
    disclaimer = Disclaimer()
    return disclaimer.delete_disclaimer(disclaimer_id)

# --------------------------- Validation ---------------------------------------- #

def validation(file_path):
    Analyzer = AnalyzeDocument()
    value, image_text = Analyzer.analyze_document(file_path=file_path)
    if value==1:
       value2, response = Analyzer.extract_value(document_text=image_text, prompt=PROMPT)
       if value2==1:
           return 1, response
       else:
           return 2, value2
    else:
        return 2, image_text
 
# ------------------------  Transcript time ---------------------------# 

def transcript(input_video):
    time_difference = Final()
    value, time = time_difference.flow(input_video)
    return value, time