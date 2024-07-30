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
Given an audio transcription in JSON format, where each word is associated with its respective start and end times, calculate the total duration of a specific sentence. The sentence of interest is:
"Mutual Fund investments are subject to market risks, read all scheme related documents carefully."

Procedure:
1. Parse the JSON transcription to extract the start and end times for each word.
2. Identify the start time of the first word "Mutual" and the end time of the last word "carefully".
3. Calculate the duration by subtracting the start time of "Mutual" from the end time of "carefully".
4. Ensure the words are part of a contiguous sentence without interruption from other sentences or breaks.
5. Provide the duration in seconds as the output in a JSON object format.

The response should strictly be a JSON object containing only the duration in seconds, formatted as following  and should not include any additional text or information as it make difficulty to parse data:
{"Time": "<calculated_time_in_seconds>"}

Example JSON transcription input for extraction:
[{'word': 'Mutual', 'start': '145.309', 'end': '145.82'}, {'word': 'fund', 'start': '145.83', 'end': '146.05'}, ...]

Ensure the sentence analysis is accurate by correctly pairing start and end times without overlapping or merging unrelated sentences.

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
