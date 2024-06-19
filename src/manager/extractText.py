from __future__ import annotations
import logging
import boto3
import psycopg2
import fitz  # PyMuPDF
from PIL import Image
import io
from src.config.credentials import aws_access_key_id, aws_secret_access_key, db_config, region_name
from src.config.queries import GET_PROGRAM_ID, GET_Rule_ID_ASSOCIATED_WITH_PROGRAM, GET_DECRIPTION_FOR_RULE_ID
from botocore.exceptions import NoCredentialsError
import os

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
            return rules_descriptions
        except Exception as e:
            logging.exception("Error fetching rules and descriptions:")
            return f"Error fetching rules and descriptions: {e}"


    def generate_prompt(self, description):
        prompt = f'''

        Please analyze the provided text and return response each time a similar word is found.
        Please give us only answers and answer in short, do not explain. If possible return answer in Yes/No.
        The output in response will be key:value pair as follows.
        Eg1:
        Rule Name : Type of risk
        Question:What is the type of risk?
        Answer:Very High Risk
        
        Eg2:
        Rule Name : Riskometer Check
        Question:Check riskometer is present or not.
        Answer:Yes
        
        Then return response like:
        Type of risk : Very High Risk
        Riskometer Check : Yes
        
        Note : Do not return word 'Rule Name' and 'Answer'. Directly return content as follows,
        Rule Name :Answer
        {description}
        '''
        
        
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
    

    def process_image_and_generate_response(self, file_path, program_type):

        try :

            bucket = 'mutual-fund-dataeaze'
            s3_file = os.path.basename(file_path)
            # Upload local file to S3 and get the S3 URL

            text_processor = ExtractText()
            s3_url = text_processor.upload_to_aws(file_path, bucket, s3_file)
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
                for description in rules_descriptions:
                    prompt = text_processor.generate_prompt(description[0])
                    content += " " + prompt

                return 1,content
        except Exception as e:
            return 2, f"An error occurred: {e}"