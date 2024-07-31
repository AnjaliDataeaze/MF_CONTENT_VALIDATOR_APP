prompt_from_config = '''

        Please analyze the provided text and return response each time a similar word is found.
        Please give us only answers and answer in Yes/No first and if yes then check the question is aking any information? if not then return Not Applicable and for answer No strictly return output Not Applicable.
        Note :  Provide a response for every rule name and question without skipping any. Every rule name and question listed in the input must have a corresponding answer and output in the response. Ensure completeness and accuracy.
                1. Do not return word 'Answer' and 'output'. 
                2. Directly return content as follows and compulsory return first Yes,No and then if explanation present for yes then add that explanation.
                3. first Analyze the question from your side and if for answer is yes then analyze fron question that does it need any explanatin? if there is no need of explanation then return Not Applicable.
                4. If question is asking for checking somthing present or not then only retun Yes/No. do not return any explanation for it.
                5. Do not add anything extra in beginning of the answer like Here are the answers based on the provided text and rules do not add this.
                6. Number of input rule name & question list should also match with answer & output list. Do not skip any rulename & disclaimer for output & answer.
        Directly return response in below mentioned format only strictly  and do not add (rule name , question) ,
        [(Answer1,output1),(Answer2,output2),(Answer3,output3)]
        [('Yes', 'Not Applicable'), ('No', 'Not Applicable'), ('Yes', 'open ended')]

        Eg1:
        Rule Name : Type of risk
        Question:What is the type of risk?
        Answer: Yes
        output : Very High Risk
        
        Eg2: (Here in this there is no need to explain the answer)
        Rule Name : Riskometer Check
        Question:Check riskometer is present or not.
        Answer:Yes
        output : NA
        
        Then return response like:
        Yes, Very High Risk
        Yes, NA
        
        For each rule name & question give answer and output. do not skip any rule name & question
        [(rule name_1, question_1),(rule name_2, question_2),(rule name_3, question_3),...]
        below are rules & questions:
        '''



prompt_template_video_frame = """
Please analyze the provided text about a mutual fund using the rules specified below and produce a JSON output for each rule.

Dictionary of Rules:
- Each rule is uniquely identified by a 'rule_id'.
- Each rule consists of a 'rule_name' and 'rule_defination' as disclaimer.

Instructions:

1. Rule Applicability Check:
   - Assess if the rule applies by determining the presence of information related to its 'rule_defination'.
   - Categorize the type of rule:
     1. Presence Verification: Rules requiring only the confirmation of information presence.
     2. Information Extraction: Rules requiring specific information to be extracted from the text.
   - If a rule is not present in context then , set 'Validation_result' to 'NO' and 'Validation_comment' to 'No Info'.
   - If a rule is Present but does not require extraction then set 'Validation_result' to 'YES' and set 'Validation_comment' to 'No Info'.
   - If a rule is Present and requires information extraction,then set 'Validation_result' to 'YES'and  provide the relevant extracted information in 'Validation-Comment'.

2. Output Structure:
   - Generate a JSON object for each rule with the following format:
   - Each rule data should be separated by ',' delimeter. It is very important to maintain the strcture output.
   - Dont generate your own rule id. 
   - Dont add extra rule information , be with respect to provided rule list.
     {{
       "rule_id": "ID of the rule",
       "rule_name": "Name of the rule",
       "rule_defination" : "Defination of rule"
       "Validation_result": "YES" or "NO",
       "Validation_comment": "No Info" or "<Extracted Information>"
     }}
   
3. Please ensure that the response strictly adheres to the specified JSON format. Dont provide any additional information in output text.
  there will only contains the data wich is described in output structure.

Detailed Rules Description:
{rules}
"""



prompt_template_audio_duration = """
Given an audio transcription provided as a list of tuples, where each tuple contains a word along with its respective start and end times, perform the following steps to calculate the total duration of the sentence: "Mutual Fund investments are subject to market risks, read all scheme related documents carefully." Follow these instructions exactly:

Procedure:
1. Parse the list of tuples to check if the full sentence "Mutual Fund investments are subject to market risks, read all scheme related documents carefully" is present and in the correct sequence.
2. If the sentence is fully present, identify the start time for "Mutual" and the end time for "carefully".
3. Calculate the sentence's duration by subtracting the start time of "Mutual" from the end time of "carefully".
4. Return the calculated duration in seconds using this JSON format only: {"Time": "<calculated_time_in_seconds>"}
5. If any part of the sentence is missing or out of order, return the error in this JSON format only: {"Error": "The specified sentence is not present in the audio transcription."}

Error Handling:
- Strictly follow the above procedure without adding any explanatory text, commentary, or additional data in the output.

Example format for input data:
[('Mutual', 'aa.a', 'bb.b'), ('Fund', 'cc.c', 'dd.d'), ('investments', 'ee.e', 'ff.f'), ..., ('carefully', 'gg.g', 'hh.h')]

Calculate the duration:
- Start time of "Mutual": aa.a
- End time of "carefully": hh.h
- Duration = end time of 'carefully' (hh.h) - start time of 'Mutual' (aa.a).

Ensure that the response contains only the necessary JSON object, reflecting either the time calculation or an error message based on the transcription analysis.

"""

source_of_truth = """
You are given two sets of data: an AI-generated output in a list format and an original result in JSON format. 
The structure of the rule provided by AI is [rule_name, rule_definition, result, validation comment]. 
Your task is to analyze the AI-generated output and compare it with the source of truth data based on the following instructions: 
1. Match Rules: For each rule in the AI-generated output, check if there is related data present in the source of truth. 
                If there is a match, check the rule's result and validation comment with the matched source of truth data. 
2. Output Format: If the rule matches and the result and validation comment match the source of truth data, 
                  return the response: 
                  {"rule_name": "AI generated rulename", 
                   "rule_defination": "AI generated", 
                   "validation_result": "AI generated result", 
                   "validation_comment": "AI generated validation comment", 
                   "source_of_truth_result": "TRUE", 
                   "source_of_truth_comment": "Verified: The data matches the source of truth."}. 
                   
                   If the rule matches but the result is wrong or different, return the response: 
                   {"rule_name": "AI generated rulename", 
                    "rule_defination": "AI generated", 
                    "validation_result": "AI generated result", 
                    "validation_comment": "AI generated validation comment", 
                    "source_of_truth_result": "FALSE", 
                    "source_of_truth_comment": "Mismatch: The data does not match the source of truth. Expected: [expected data]."} 
                    
                  If there is no match in the rule, return the response: 
                  {"rule_name": "AI generated rulename", 
                   "rule_defination": "AI generated", 
                   "validation_result": "AI generated result", 
                   "validation_comment": "AI generated validation comment", 
                   "source_of_truth_result": "Not Applicable", 
                   "source_of_truth_comment": "No Comment"}. 
                   
3. Detailed Steps: Iterate over each rule in the AI-generated list. 
   For each rule, identify the related field in the source of truth. 
   Compare the data: If a match is found, set "source_of_truth_result" to "TRUE" if the data matches or "FALSE" if it does not. 
   If no match is found, set "source_of_truth_result" to "Not Applicable". Generate the output according to the provided format. 
   Instructions: 1. Follow the steps and rules provided to analyze the data. 
                 2. Ensure the output adheres to the specified format. 
                 3. Validate the results and include specific comments explaining why the data matches or does not match. 
                 4. Return only the JSON response without any additional explanation or details."
"""
