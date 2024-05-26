
PROMPT = '''Task: Analyze the provided document text and provide the following details.
            1. Check if the following  exact terms are appeares in text: 
                ["Riskometer", "Mutual Fund investments are subject to market risks" appears in the text.]
                If given text appears then return "Yes" otherwise return "No".
            2. Check  Type of Risk i.e "Low", "Low to Moderate", "Moderate", "Moderately High", "High", "Very High" like word are present.
            3. Check fund type i.e. open-ended or close-ended or any other. 
            4. Give all the name of the fund manager, or Managing Director.
            5. If any details/ terms are  not present or not mentioned then stictly return "No" in output.
            6. Output Format: Provide the output in pure JSON format, adhering to the specified structure:
               {"Riskometer":"Yes or No", "Mutual Fund investments are subject to market risks": "Yes or No", "Risk": "Enter Risk Type", "Fund Type": "Enter the fund type","Fund Manager" : "Enter Fund Manager Details"}

            '''

QUESTIONS = ''' Scheme Riskometer present in text?
                Benchmark Riskometer present in text?
                Mutual Fund investments are subject to market risks is present in extracted text?
                What is the type of Risk?
                What is the type of fund?
                What are the details of fund manager?'''