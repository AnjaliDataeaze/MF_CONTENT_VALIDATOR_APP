from __future__ import annotations
from botocore.exceptions import ClientError
from PIL import Image
from datetime import datetime
from typing import List
import boto3
import json
import logging
import psycopg2
import fitz  # PyMuPDF
import io
import os
import ast
import imageio
import numpy as np
import cv2
from botocore.exceptions import NoCredentialsError
from src.config.credentials import aws_access_key_id, aws_secret_access_key, db_config, region_name
from src.config.queries import GET_PROGRAM_ID, GET_Rule_ID_ASSOCIATED_WITH_PROGRAM, GET_DECRIPTION_FOR_RULE_ID, RETURN_OUTPUT, CREATE_SEQUENCE_GROUP_ID,NEXTVAL_GROUP_ID
from src.config.prompts import prompt_from_config, source_of_truth

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

s3 = boto3.client(
    's3',
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key = aws_secret_access_key,
    region_name = region_name
)

class ExtractText:
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
        
    @staticmethod
    def fetch_rules_and_descriptions(program_name):
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
            # print(rules_descriptions)
            return rules_descriptions
        except Exception as e:
            logging.exception("Error fetching rules and descriptions:")
            return f"Error fetching rules and descriptions: {e}"

    @staticmethod
    def generate_prompt(description):
        prompt = f"{prompt_from_config}\n{description}"
        return prompt
    
    @staticmethod
    def extract_text_from_image(image_path):
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
    
    @staticmethod
    def convert_pdf_to_images(pdf_path):
        # Open the PDF file
        document = fitz.open(pdf_path)
        images = []
        for page_number in range(len(document)):
            page = document.load_page(page_number)
            zoom = 3
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            #pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            image_bytes = io.BytesIO()
            img.save(image_bytes, format='PNG')
            images.append(image_bytes.getvalue())
        
        return images

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        images = ExtractText().convert_pdf_to_images(pdf_path)
        all_text = ""

        for image in images:
            # Call AWS Textract
            response = textract.detect_document_text(Document={'Bytes': image})
            
            # Extract detected text
            for item in response["Blocks"]:
                if item["BlockType"] == "LINE":
                    all_text += item["Text"] + "\n"
        
        return all_text
    
    @staticmethod
    def generate_message(bedrock_runtime, model_id, system_prompt, messages, max_tokens):

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
    

    @staticmethod
    def generate_response(input_text):
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
            max_tokens = 4000

            # Prompt with user turn only.
            user_message =  {"role": "user", "content": input_text}
            messages = [user_message]

            response = ExtractText().generate_message(bedrock_runtime, model_id, system_prompt, messages, max_tokens)
            # print(json.dumps(response, indent=4))

            single_string = response  # Use the response text directly
            return single_string
        
        except ClientError as err:
            message=err.response["Error"]["Message"]
            logger.error("A client error occurred: %s", message)
            print("A client error occured: " +
                format(message))
            return None
        
    @staticmethod
    def return_output(group_id):
        # Fetch the inserted data for frontend display
        try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        RETURN_OUTPUT,
                        (group_id,)
                    )
                    rows = cursor.fetchall()

                    data = []
                    for row in rows:
                        data.append([row[0], row[1], row[2], row[3]])

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
            if s3_url is None:
                return
            
            if s3_url.lower().endswith('.pdf'):
                extracted_text = text_processor.extract_text_from_pdf(file_path)
            else:
                extracted_text = text_processor.extract_text_from_image(file_path)

            rules_descriptions = text_processor.fetch_rules_and_descriptions(program_type)

            if isinstance(rules_descriptions, str):
                return rules_descriptions  # Return the error message
            else:
                content = extracted_text
                prompt = text_processor.generate_prompt(rules_descriptions)
                content += " " + prompt

            results = text_processor.generate_response(content)

            document_link = f"{s3_url}_{datetime.now().isoformat()}"
            if isinstance(results, str):
                try:
                    results = ast.literal_eval(results)
                    print("-------------",results)
                except (ValueError, SyntaxError) as e:
                    print(f"Failed to parse results: {e}")

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
                        print("rule-tuple",rule_tuple)
                        rulename = rule_tuple[0]
                        print(rulename)
                        rule = rule_tuple[1]
                        print(rule)
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
        

    def compare_with_SOT(self, data, dataset_name, lk_value):
        try:
            cursor.execute("""
                            SELECT m.col_name, m.col_value
                            FROM ref_dset_records m
                            INNER JOIN ref_dset_master r ON r.id = m.type_id
                            WHERE m.lk_colvalue = %s AND r.dset_name = %s """, (lk_value, dataset_name,))
            row = cursor.fetchall()

            result_dict = {item[0]: item[1] for item in row}
            result_json = json.dumps(result_dict, indent=4)

            
            prompt =   f"AI Generated Data >>> {data}  + '\n' + Original Data >> {result_json} + '\n' + Instruction >>>{source_of_truth}"
            response = ExtractText.generate_response(prompt)
            response_json = json.loads(response)    
            return 1, response_json
        except Exception as e:
            return 2, str(e)


    
#==========================================================================================================
#==========================================================================================================
#==========================================================================================================

    @staticmethod
    def get_frame(gif_path):
        s3_bucket_name = "mutual-fund-dataeaze"
        s3_folder = 'GIF'
        gif = imageio.mimread(gif_path)
        fps = 10  # GIFs usually don't have a defined FPS, so you may need to set it manually
        
        # Upload the original GIF file to S3
        try:
            s3_file = os.path.basename(gif_path)
            s3.upload_file(gif_path, s3_bucket_name, f'{s3_folder}/{s3_file}')
            print(f'Uploaded original GIF to s3://{s3_bucket_name}/{s3_folder}/{s3_file}')
        except FileNotFoundError:
            print(f'The file {gif_path} was not found.')
        except NoCredentialsError:
            print('Credentials not available.')

        prev_frame = None
        frame_differences = []

        # Read frames from the GIF
        for frame in gif:
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2GRAY)
            if prev_frame is not None:
                # Calculate the absolute difference between current frame and previous frame
                diff = cv2.absdiff(prev_frame, frame)
                frame_differences.append(np.sum(diff))  # Sum of all pixel differences
            prev_frame = frame

        # Convert frame differences to a more manageable scale
        frame_differences = np.array(frame_differences) / 1e6

        # Threshold for 'no drastic change'
        change_threshold = 0.8  # Adjust based on your video and needs

        # Find stable intervals
        stable_intervals = []
        start_frame = 0

        for i, diff in enumerate(frame_differences):
            if diff > change_threshold:
                if start_frame < i - 1:
                    # End of a stable interval
                    end_frame = i
                    start_time = start_frame / fps
                    end_time = end_frame / fps
                    stable_intervals.append((start_time, end_time))
                # Start of a new possible stable interval
                start_frame = i + 1

        # Add the last stable interval if the end of the video is stable
        if start_frame < len(frame_differences) - 1:
            end_time = len(frame_differences) / fps
            start_time = start_frame / fps
            stable_intervals.append((start_time, end_time))

        
        for i, (start_time, end_time) in enumerate(stable_intervals):
            end_frame = int(end_time * fps)
            
            if end_frame < len(gif):
                frame = gif[end_frame]
                frame_bgr = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)  # Convert to BGR format for saving with OpenCV
                
                output_path = f'frame_{i+1}.png'
                cv2.imwrite(output_path, frame_bgr)
                print(f'Saved frame at {end_time:.2f} seconds to {output_path}')
                
                # Upload the frame to S3
                try:
                    s3.upload_file(output_path, s3_bucket_name, f'{s3_folder}/{output_path}')
                    print(f'Uploaded {output_path} to s3://{s3_bucket_name}/{s3_folder}/{output_path}')
                except FileNotFoundError:
                    print(f'The file {output_path} was not found.')
                except NoCredentialsError:
                    print('Credentials not available.')

            else:
                print(f'End frame {end_frame} is out of range for the GIF with {len(gif)} frames.')
        return 1 ,  f"s3://{s3_bucket_name}/{s3_folder}/original_gif.gif"
    
    
    @staticmethod
    def extract_text_from_gif_image(image_bytes):
        response = textract.detect_document_text(Document={'Bytes': image_bytes})
        text = ""
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                text += item["Text"] + "\n"
        return text
    
    @staticmethod
    def text_form_gif_images(s3_bucket_name,s3_folder):
    
        response = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_folder)
        image_files = [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith(('jpg', 'jpeg', 'png'))]
        combined_text = ""
        for file_key in image_files:
            obj = s3.get_object(Bucket=s3_bucket_name, Key=file_key)
            image_bytes = obj['Body'].read()
            img_text = ExtractText().extract_text_from_gif_image(image_bytes=image_bytes)
            combined_text += img_text + " "
        return combined_text  

    def process_gif(self,file_path, program_type):
        val, s3_url= ExtractText().get_frame(file_path)
        s3_bucket_name = "mutual-fund-dataeaze"
        s3_folder = 'GIF'
        if val ==1:
            image_text = ExtractText().text_form_gif_images(s3_bucket_name, s3_folder)
            print("IMAGE_TEXT----->", image_text)
            rules_descriptions = ExtractText().fetch_rules_and_descriptions(program_type)
            print("RULE*******************************")
            print("RULE Description-->", rules_descriptions)

            if isinstance(rules_descriptions, str):
                return rules_descriptions  # Return the error message
            else:
                content = image_text
                prompt = ExtractText().generate_prompt(rules_descriptions)
                content += " " + prompt

            results = ExtractText().generate_response(content)

            # Construct the document_link with s3_url and current timestamp
            document_link = f"{s3_url}_{datetime.now().isoformat()}"

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

                final_result = ExtractText().return_output(group_id)  
                return 1, final_result  
            
            except Exception as e:
                logging.exception("Error in adding output to the database")
                return f"Error adding output to the database: {e}"
            

