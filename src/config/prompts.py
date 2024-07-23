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
- Each rule consists of a 'rule_name' and 'rule_definition'.

Instructions:

1. Rule Applicability Check:
   - Assess if the rule applies by determining the presence of information related to its 'rule_definition'.
   - Categorize the type of rule:
     1. Presence Verification: Rules requiring only the confirmation of information presence.
     2. Information Extraction: Rules requiring specific information to be extracted from the text.
   - If a rule is not applicable, set 'Applicable' to 'NO' and 'result' to 'No Info'.
   - If a rule is applicable but does not require extraction, set 'result' to 'No Info'.
   - If a rule is applicable and requires information extraction, provide the relevant extracted information in 'result'.

2. Output Structure:
   - Generate a JSON object for each rule with the following format:
   - Each rule data should be separated by ',' delimeter. It is very important to maintain the strcture output.
   - Dont generate your own rule id. 
   - Dont add extra rule information , be with respect to provided rule list.
     {{
       "rule_id": "ID of the rule",
       "rule_name": "Name of the rule",
       "Applicable": "YES" or "NO",
       "result": "No Info" or "<Extracted Information>"
     }}
   
3. Please ensure that the response strictly adheres to the specified JSON format. Dont provide any additional information in output text.
  there will only contains the data wich is described in output structure.

Detailed Rules Description:
{rules}
"""




prompt_template_audio = """Analyzed the provided audio transcription and verify the following rules and provide the information.

                             The provide text is of  audio transcription of mutual fund .:
                             There are two type of text:
                             1) PLAIN_TRANSCRIPT: A plain text.
                             2) JSON_TRANSCRIPT : Text which is with word and there start and end timestamp.
                             Use JSON_TRANSCRIPT to find the legth in second  of provided sentence .
                             Plese refer JSON_TRANSCRIPT to find out sentence length and use PLAIN_TRANSCRIPT for other rules.

                          1. Output Structure:
                            - Generate a JSON object for each rule with the following format:
                            - Each rule data should be separated by ',' delimeter. It is very important to maintain the strcture output.
                              {{
                                "rule_id": "ID of the rule",
                                "rule_name": "Name of the rule",
                                "Applicable": "YES" or "NO",
                                "result": "Time in seconds"
                              },
                              {
                                "rule_id": "ID of the rule",
                                "rule_name": "Name of the rule",
                                "Applicable": "YES" or "NO",
                                "result": "No Info" or "<Extracted Information>"
                              }}
                          3. Please ensure that the response strictly adheres to the specified JSON format. Dont provide any additional information in output text.
                            there will only contains the data wich is described in output structure.

                          Detailed Rules Description:
                          {rules} 
"""



prompt_template_audio_duration = """
Given the audio transcription in JSON format, which includes words along with their respective start and end times, calculate the total duration of a specific sentence. The sentence of interest is:
"Mutual Fund investments are subject to market risks, read all scheme related documents carefully."

Procedure:
1. Identify the start time of the first word "Mutual" and the end time of the last word "carefully".
2. Calculate the duration by subtracting the start time of "Mutual" from the end time of "carefully".
3. Provide the duration in seconds as the output.

The response should strictly be a JSON object with the duration in seconds and should not include any additional text or information.

Example JSON Output Format:
{"Time": "<calculated_time_in_seconds>"}

Use the JSON transcription provided to extract the necessary timings for the calculation.
"""
