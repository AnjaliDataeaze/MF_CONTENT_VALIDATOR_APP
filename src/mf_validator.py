# mf_validator.py
from src.manager.program import Program
from src.manager.rules import Rules
from src.manager.disclaimer import Disclaimer
# from src.manager.validation import AnalyzeDocument
# from src.config.prompts import PROMPT
# from src.manager.transcription import Final
from src.manager.validation import ExtractText
from src.manager.transcription import Transcrib
# class validator:
def add_program(name, description, rules):
    program = Program(name, description, rules)
    return program.add_program()

def list_programs():
    return Program.list_programs()

def edit_program(program_id, name, description, rules):

    program = Program("", "", "")
    return program.edit_program(program_id, name, description, rules)


def delete_program(program_id):
    program = Program("", "", "" )
    return program.delete_program(program_id)

# ------------------------------------------------------------#


def add_rule(rulename, media_type, description, disclaimer):
    rule = Rules(rulename, media_type, description, disclaimer)
    return rule.add_rule()

def list_rules():
    return Rules.list_rules()

def edit_rule(rule_id, rulename, description, disclaimer):
    rule = Rules("", "", "", "")
    return rule.edit_rule(rule_id, rulename, description, disclaimer)

def delete_rule(rule_id):
    rule = Rules("","", "", "")
    return rule.delete_rule(rule_id)

def list_rules_by_program(program_id):
    return Rules.list_rules_by_program(program_id)

def get_mapped_rules(program_id):
    rule = Rules("","", "", "")
    return rule.get_mapped_rules(program_id)

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


def validation(file_path, program_type):

    extract1 = ExtractText()
    value, results = extract1.process_image_and_generate_response(file_path=file_path, program_type=program_type)
    if value == 1:
        return 1, results

def gif_validation(file_path, program_type):
    extract1 = ExtractText()
    value, results = extract1.process_gif(file_path=file_path, program_type=program_type)
    if value == 1:
        return 1, results

# ------------------------  Transcript time ---------------------------# 

# def transcript(input_video):
#     time_difference = Final()
#     value, time = time_difference.flow(input_video)
#     return value, time

def transcript(input_video):
    time_difference = Transcrib()
    value, time = time_difference.duration(input_video)
    return value, time
