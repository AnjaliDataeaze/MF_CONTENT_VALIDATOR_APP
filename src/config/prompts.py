prompt_from_config = '''

        Please analyze the provided text and return response each time a similar word is found.
        Please give us only answers and answer in Yes/No first and if yes then check the question is aking any information? if not then return Not Applicable and for answer No strictly return output Not Applicable.
        Note :  1. Do not return word 'Answer' and 'output'. 
                2. Directly return content as follows and compulsory return first Yes,No and then if explanation present for yes then add that explanation.
                3. first Analyze the question from your side and if for answer is yes then analyze fron question that does it need any explanatin? if there is no need of explanation then return Not Applicable.
                4. If question is asking for checking somthing present or not then only retun Yes/No. do not return any explanation for it.
                5. Do not add anything extra in beginning of the answer like Here are the answers based on the provided text and rules do not add this. 
        Directly return response in below format and do not add (rule name , question) ,
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