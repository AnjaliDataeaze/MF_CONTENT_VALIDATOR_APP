
PROMPT = '''Please analyze the provided document and return response each time similar word is found.
            Please give us only answers and answer in short do not explain.
            check if the exact terms "Riskometer", "Mutual Fund investments are subject to market risks" appears in the text.
            Check  Low, Low to Moderate, Moderate, Moderately High, High, Very High like word are present if not present or not mentioned then return only No.
            Check fund type i.e. open-ended or close-ended or any other if not present or not mentioned then return only No.
            Give all the name of the fund manager, or Managing Director if not present or not mentioned then return only No.
            The output in response will be key:value pair as following.
            Riskometer : Yes/No
            Mutual Fund investments are subject to market risks : Yes/No
            Risk : return risk type like Low, Low to Moderate, Moderate, Moderately High, High, Very High
            Fund Type : answer
            Fund Manager : Details
            '''

QUESTIONS = ''' Scheme Riskometer present in text?
                Benchmark Riskometer present in text?
                Mutual Fund investments are subject to market risks is present in extracted text?
                What is the type of Risk?
                What is the type of fund?
                What are the details of fund manager?'''