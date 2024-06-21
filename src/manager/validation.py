from __future__ import annotations
import boto3
import json
import logging
from botocore.exceptions import ClientError
import psycopg2
import fitz  # PyMuPDF
from PIL import Image
import io
from src.config.credentials import aws_access_key_id, aws_secret_access_key, db_config, region_name
from src.config.queries import GET_PROGRAM_ID, GET_Rule_ID_ASSOCIATED_WITH_PROGRAM, GET_DECRIPTION_FOR_RULE_ID, RETURN_OUTPUT, CREATE_SEQUENCE_GROUP_ID,NEXTVAL_GROUP_ID, INSERT_OUTPUT
from src.config.prompts import prompt_from_config
from botocore.exceptions import NoCredentialsError
import os
from datetime import datetime
import ast
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()


# Initialize the boto3 client for Textract
textract = boto3.client(
    'textract',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)


class ExtractText:
    # def __init__(self, db_config):
    #     self.conn = psycopg2.connect(**db_config)
    @staticmethod
    def upload_to_aws(local_file, bucket, s3_file):
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
           
        try:
            s3.upload_file(local_file, bucket, s3_file)

            return f"s3://{bucket}/{s3_file}"
        except FileNotFoundError:
            print("The file was not found")
            return None
        except NoCredentialsError:
            print("Credentials not available")
            return None

    def fetch_rules_and_descriptions(self, program_name):
        try:
            with conn.cursor() as cursor:
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
            print(rules_descriptions)
            return rules_descriptions
        except Exception as e:
            logging.exception("Error fetching rules and descriptions:")
            return f"Error fetching rules and descriptions: {e}"


    def generate_prompt(self, description):

        prompt = f"{prompt_from_config}\n{description}"
        return prompt

    def extract_text_from_image(self, image_path):
        # Read image file
        with open(image_path, 'rb') as document:
            image_bytes = document.read()
        
        # Call AWS Textract
        response = textract.detect_document_text(Document={'Bytes': image_bytes})
        
        # Extract detected text
        text = ""
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                text += item["Text"] + "\n"
        
        return text
    
    def convert_pdf_to_images(self, pdf_path):
        # Open the PDF file
        document = fitz.open(pdf_path)
        images = []
        for page_number in range(len(document)):
            page = document.load_page(page_number)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            image_bytes = io.BytesIO()
            img.save(image_bytes, format='PNG')
            images.append(image_bytes.getvalue())
        
        return images

    def extract_text_from_pdf(self, pdf_path):
        images = self.convert_pdf_to_images(pdf_path)
        all_text = ""

        for image in images:
            # Call AWS Textract
            response = textract.detect_document_text(Document={'Bytes': image})
            
            # Extract detected text
            for item in response["Blocks"]:
                if item["BlockType"] == "LINE":
                    all_text += item["Text"] + "\n"
        
        return all_text
    
        
    def generate_message(self,bedrock_runtime, model_id, system_prompt, messages, max_tokens):

        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": messages
            }  
        )  
        
        response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
        # response_body = json.loads(response.get('body').read())
        response_body_str = response.get('body').read()
        response_body = json.loads(response_body_str)
        text_value = response_body['content'][0]['text']

        return text_value

    def generate_response(self,input_text):
        """
        Entrypoint for Anthropic Claude message example.
        """
        __aws_secret_access_key:str = aws_secret_access_key
        __aws_access_key_id:str = aws_access_key_id
        __region_name:str = region_name
        try:

            bedrock_runtime = boto3.client(service_name='bedrock-runtime', aws_access_key_id=__aws_access_key_id, 
                    aws_secret_access_key=__aws_secret_access_key,
                    region_name=__region_name)

            model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
            system_prompt = "Answer the question from given content."
            max_tokens = 1000

            # Prompt with user turn only.
            user_message =  {"role": "user", "content": input_text}
            messages = [user_message]

            response = self.generate_message(bedrock_runtime, model_id, system_prompt, messages, max_tokens)
            # print(json.dumps(response, indent=4))

            single_string = response  # Use the response text directly
            return single_string
        
        except ClientError as err:
            message=err.response["Error"]["Message"]
            logger.error("A client error occurred: %s", message)
            print("A client error occured: " +
                format(message))
            return None
    
    def return_output(self,group_id):
        # Fetch the inserted data for frontend display
        try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        RETURN_OUTPUT,
                        (group_id,)
                    )
                    rows = cursor.fetchall()

                    # Format the data as required for frontend
                    data = []
                    for row in rows:
                        data.append([row[0], row[1], row[2], row[3]])
                    print(data)
                    return data
        except Exception as e:
                logging.exception("Error in adding output to the database")
                return f"Error adding output to the database: {e}"

    def process_image_and_generate_response(self, file_path, program_type):
        try:
            bucket = 'mutual-fund-dataeaze'
            s3_file = os.path.basename(file_path)

            # Upload local file to S3 and get the S3 URL
            text_processor = ExtractText()
            s3_url = text_processor.upload_to_aws(file_path, bucket, s3_file)
            print(s3_url)
            if s3_url is None:
                return

            if s3_url.lower().endswith('.pdf'):
                extracted_text = text_processor.extract_text_from_pdf(file_path)
            else:
                extracted_text = text_processor.extract_text_from_image(file_path)

            # Fetch rules and descriptions
            rules_descriptions = text_processor.fetch_rules_and_descriptions(program_type)
            if isinstance(rules_descriptions, str):
                return rules_descriptions  # Return the error message
            else:
                content = extracted_text
                prompt = text_processor.generate_prompt(rules_descriptions)
                content += " " + prompt

            results = text_processor.generate_response(content)

            # Construct the document_link with s3_url and current timestamp
            document_link = f"{s3_url}_{datetime.now().isoformat()}"
            print(document_link)

            if isinstance(results, str):
                results = ast.literal_eval(results)


            # Check if lengths of rules_descriptions and results match
            if not isinstance(results, list) or len(rules_descriptions) != len(results):

                raise ValueError("Mismatch between number of rules and results")

            # Additional debug: print each element in results to check its structure
            for i, result in enumerate(results):
                print(f"Result {i}: {result}, Length: {len(result)}")

            try:
                with conn.cursor() as cursor:
                    # Generate a unique group_id
                    cursor.execute(CREATE_SEQUENCE_GROUP_ID)

                    cursor.execute(NEXTVAL_GROUP_ID)
                    group_id = cursor.fetchone()[0]

                    # Insert rules_descriptions into the table
                    for i, rule_tuple in enumerate(rules_descriptions):
                        rulename = rule_tuple[0]
                        rule = rule_tuple[1]
                        answer = results[i][0]
                        output = results[i][1]

                        # print(f"Inserting rule: group_id: {group_id}, document_link: {document_link}, rulename: {rulename}, rule: {rule}, answer: {answer}, output: {output}")

                        cursor.execute(
                            INSERT_OUTPUT,
                            (group_id, document_link, rulename, rule, answer, output,'pdf/image')
                        )

                    # Commit the transaction for rules_descriptions
                    conn.commit()
                    logging.info("Data committed to the database")

                final_result = text_processor.return_output(group_id)  
                return 1, final_result  
            
            except Exception as e:
                logging.exception("Error in adding output to the database")
                return f"Error adding output to the database: {e}"


        except Exception as e:
            logging.exception("An error occurred during the processing")
            return 2, f"An error occurred: {e}"