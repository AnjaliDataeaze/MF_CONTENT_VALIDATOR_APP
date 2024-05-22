# mf_validator.py


from src.manager.program import Program
from src.manager.rules import Rules
from src.manager.disclaimer import Disclaimer

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

def add_rule(rulename, media_type, description, program_id):
    rule = Rules(rulename, media_type, description, program_id)
    return rule.add_rule()

def list_rules():
    return Rules.list_rules()

def edit_rule(rule_id, rulename, media_type, description):
    rule = Rules("", "", "", "")
    return rule.edit_rule(rule_id, rulename, media_type, description)

def delete_rule(rule_id):
    rule = Rules("", "", "", "")
    return rule.delete_rule(rule_id)

def list_rules_by_program(program_id):
    return Rules.list_rules_by_program(program_id)

def add_disclaimer(name_of_disclaimer, rule_id, actual_disclaimer):
    disclaimer = Disclaimer(name_of_disclaimer, rule_id, actual_disclaimer)
    return disclaimer.add_disclaimer()

def list_disclaimers():
    return Disclaimer.list_disclaimers()

def edit_disclaimer(disclaimer_id, rule_id, actual_disclaimer):
    disclaimer = Disclaimer("", "", "")
    return disclaimer.edit_disclaimer(disclaimer_id, rule_id, actual_disclaimer)

def delete_disclaimer(disclaimer_id):
    disclaimer = Disclaimer("", "", "")
    return disclaimer.delete_disclaimer(disclaimer_id)



# if __name__ == "__main__":
#     print(add_program("Python", "A high-level programming language"))
#     print(add_program("Java", "An object-oriented programming language"))
#     print(list_programs())
#     print(edit_program("Java", "Java", "A widely-used programming language"))
#     print(list_programs())
#     print(delete_program("Python"))
#     print(list_programs())
