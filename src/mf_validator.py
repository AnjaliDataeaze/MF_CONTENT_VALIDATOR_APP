# mf_validator.py
from src.manager.program import Program
from src.manager.rules import Rules
from src.manager.disclaimer import Disclaimer
# from src.manager.validation import AnalyzeDocument
# from src.config.prompts import PROMPT
from src.manager.source_of_truth import Source_of_Truth
from src.manager.validation import ExtractText
from src.manager.transcription import Transcrib


from src.manager.video_validation import VideoProcessor, S3ImageProcessor, Get_Image_url
# class validator:


def add_program(name, description, rules, created_by):
    return Program.add_program(name, description, rules, created_by)

def list_programs():
    return Program.list_programs()

def edit_program(program_id, name, description, rules):
    return Program.edit_program(program_id, name, description, rules)


def delete_program(program_id):
    return Program.delete_program(program_id)


# ------------------------------------------------------------#


def add_rule(rulename, media_type, description, disclaimer, assigned_to, ruleStatus, created_by):
    return Rules.add_rule(rulename, media_type, description, disclaimer, assigned_to, ruleStatus, created_by)

def list_rules(status):
    return Rules.list_rules(status)

def filter_rules(search, status=None):
    return Rules.filter_rules(search, status)

def edit_rule(rule_id, rulename, description, disclaimer):
    return Rules.edit_rule(rule_id, rulename, description, disclaimer)

def delete_rule(rule_id):
    return Rules.delete_rule(rule_id)

def get_mapped_rules(program_id):
    return Rules.get_mapped_rules(program_id)

def change_rule_status(rule_id, status):
    return Rules.change_rule_status(rule_id, status)
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


def validation(file_path, program_type, dataset_name, scheme_name ):
    extract1 = ExtractText()
    value, results = extract1.process_image_and_generate_response(file_path=file_path, program_type=program_type)

    if value == 1:
        value1, result1 = extract1.compare_with_SOT(data= results, dataset_name=dataset_name, lk_value = scheme_name )
        return value1, result1 
    
    else:
        return value, results

def gif_validation(file_path, program_type):
    extract1 = ExtractText()
    value, results = extract1.process_gif(file_path=file_path, program_type=program_type)
    if value == 1:
        return 1, results


# ------------------------  Transcript time ---------------------------# 

def transcript(input_video, program_type):
    transcription = Transcrib()
    return transcription.process_audio_transcription(input_video,program_type)
     

def frame_analysis(input_video, program_type):
    frame = VideoProcessor(input_video)
    frame.process_video()
    image  = S3ImageProcessor(program_type=program_type)
    data = image.process_images()
    return data

#--------------------source of truth -----------------# 

def source_of_truth(csv_file_path, dataset_name, description, lookup_key_colname):
    sot = Source_of_Truth()
    return  sot.upload_csv_to_db(csv_file_path, dataset_name, description, lookup_key_colname)
    
def list_dataset():
    sot = Source_of_Truth()
    return sot.list_dataset()

def list_dataset_info():
    sot = Source_of_Truth()
    return sot.list_dataset_info()

def list_dataset_records(type_id):
    sot = Source_of_Truth()
    return sot.list_dataset_records(type_id)

def list_scheme(dataset_name):
    sot = Source_of_Truth()
    return sot.list_scheme(dataset_name)