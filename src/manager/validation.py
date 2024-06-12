from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from openai import AzureOpenAI
from src.config.credentials import endpoint, endpoint_key, api_key, api_version, azure_endpoint
import json
import psycopg2
from src.config.credentials import db_config
from src.config.queries import GET_PROGRAM_ID,GET_Rule_ID_ASSOCIATED_WITH_PROGRAM, GET_DECRIPTION_FOR_RULE_ID
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)

credential = AzureKeyCredential(endpoint_key)
document_analysis_client = DocumentAnalysisClient(endpoint, credential)
 

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()

    
class AnalyzeDocument:
    
    def analyze_document(self, file_path):
        try:
            with open(file_path, "rb") as file:
                document_data = file.read()

            poller = document_analysis_client.begin_analyze_document("prebuilt-idDocument", document_data)
            result = poller.result()

            text_data = []
            for page in result.pages:
                for line in page.lines:
                    text_data.append(line.content)
            document_text = ', '.join(text_data)
            print("DONE with text extracting")
            return 1, document_text
        except Exception as e:
            return 2, f"Error: {e}"

    def fetch_rules_and_descriptions(self, program_name):
        try:
            with self.conn.cursor() as cursor:
                # Get the program ID for the given program name
                cursor.execute(GET_PROGRAM_ID, (program_name,))
                program_id = cursor.fetchone()
                if not program_id:
                    return f"Error: Program '{program_name}' not found"
                program_id = program_id[0]

                # Get the rules IDs associated with the program
                cursor.execute(GET_Rule_ID_ASSOCIATED_WITH_PROGRAM, (program_id,))
                rule_ids = cursor.fetchall()
                if not rule_ids:
                    return f"Error: No rules found for program '{program_name}'"

                # Get the descriptions for the rules IDs
                rules_descriptions = []
                for rule_id in rule_ids:
                    cursor.execute(GET_DECRIPTION_FOR_RULE_ID, (rule_id,))
                    rules_descriptions.extend(cursor.fetchall())

            return rules_descriptions
        except Exception as e:
            return f"Error fetching rules and descriptions: {e}"

    def generate_prompt(self, description):
        prompt = f'''

        Please analyze the provided document and return response each time a similar word is found.
        Please give us only answers and answer in short, do not explain. 
        The output in response will be key:value pair as follows. Note Start giving output from Product Riskometer directly do not add any word other than below in start or end of the response.
        {description} : Yes/No
        '''

        
        return prompt

    def extract_value(self, document_text, prompt):
        document_text_str = json.dumps(document_text)
        prompt_str = json.dumps(prompt)
        content = document_text_str + "\n" + prompt_str
        user_message = {
            "role": "user",
            "content": content
        }

        conversation = [
            {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
            user_message
        ]

        try:
            response = client.chat.completions.create(
                model="v-ai-turbo",
                messages=conversation
            )

            responses = {choice.message.content for i, choice in enumerate(response.choices)}

            return 1, responses
        except Exception as e:
            return 2, f"An error occurred: {e}"
        
    
    def process_document(self, file_path, program_name, media_type):
        if media_type.lower() in ["pdf", "image"]:
            status, document_text = self.analyze_document(file_path)
            if status != 1:
                return document_text  # Return the error message

            rules_descriptions = self.fetch_rules_and_descriptions(program_name)
            if isinstance(rules_descriptions, str):
                return rules_descriptions  # Return the error message

            results = []
            for rule_id, description in rules_descriptions:
                prompt = self.generate_prompt(description)
                print("-----------------------------------------")
                print("----Prompt----------",prompt)
                print("-----------------------------------------")
                status, response = self.extract_value(document_text, prompt)
                if status != 1:
                    results.append(response)  # Append the error message
                else:
                    results.append(response)

            return results

        return "Unsupported media type"