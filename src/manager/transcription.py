import re
import os
from src.config.credentials import db_config,region_name, aws_access_key_id, aws_secret_access_key, S3_BUCKET
from src.config.queries import PROGRAM_ID, SELECT_RULES_BY_PROGRAM_AUDIO
from src.config.prompts import prompt_template_video_frame, prompt_template_audio_duration
from botocore.exceptions import NoCredentialsError
import boto3
import time
import json
import urllib.request
import psycopg2
import datetime
try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()

# Function to upload a local file to AWS S3
class Transcrib:
    @staticmethod
    def upload_to_aws(local_file, s3_file):
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

        try:
            s3.upload_file(local_file, S3_BUCKET, s3_file)
            print("Upload Successful")
            return f"s3://{S3_BUCKET}/{s3_file}"
        except FileNotFoundError:
            print("The file was not found")
            return None
        except NoCredentialsError:
            print("Credentials not available")
            return None

    # Function to start the transcription job
    @staticmethod
    def start_transcription_job(job_name, job_uri, language_code):
        transcribe = boto3.client('transcribe', 
                                region_name=region_name, 
                                aws_access_key_id=aws_access_key_id, 
                                aws_secret_access_key=aws_secret_access_key)

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='mp4',  # or 'mp4', 'wav', 'flac'get_transcription_job
            LanguageCode=language_code
        )

        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print("Not ready yet...")
            time.sleep(10)


        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcription_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']

            with urllib.request.urlopen(transcription_url) as response:
                transcription_result = json.loads(response.read().decode())

            plain_transcript = transcription_result['results']['transcripts'][0]['transcript']

            words_times = []
            for item in transcription_result['results']['items']:
                if item['type'] == 'pronunciation':
                    word = item['alternatives'][0]['content']
                    start_time = item['start_time']
                    end_time = item['end_time']
                    words_times.append((word, start_time, end_time))

            return plain_transcript, words_times

    
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
            response_body_str = response.get('body').read()
            
            response_body = json.loads(response_body_str)
            text_value = response_body['content'][0]['text']
            return text_value

    @staticmethod
    def generate_response(input_text):
            
        bedrock_runtime = boto3.client(service_name='bedrock-runtime',
                        region_name=region_name, 
                        aws_access_key_id = aws_access_key_id, 
                        aws_secret_access_key = aws_secret_access_key)

        model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        system_prompt = "Answer the question from given content."
        max_tokens = 1000

        # Prompt with user turn only.
        user_message =  {"role": "user", "content": input_text}
        messages = [user_message]

        response =Transcrib().generate_message(bedrock_runtime, model_id, system_prompt, messages, max_tokens)
        return response


    @staticmethod
    def list_rules(program_type):
        try:    
            cursor.execute(PROGRAM_ID, (program_type,))
            program_id_result = cursor.fetchone()
            program_id = program_id_result[0] 
            cursor.execute(SELECT_RULES_BY_PROGRAM_AUDIO, (program_id,))

            rules = cursor.fetchall()
            if len(rules) == 0:
                return None
            else:
                dictionary = {item[0]: (item[1], item[2]) for item in rules}
                return dictionary           
        except Exception as e:
            return None


    @staticmethod
    def prompt_for_audio_rule(trancript,  prompt_template1 ):
            prompt = f"Trancript-->{trancript}\n INSTRUCTION-->{prompt_template1}"
            return prompt

    def process_audio_transcription(self, file, program_type):
        s3_file = os.path.basename(file)
        s3_url = Transcrib().upload_to_aws(file, s3_file)
        if s3_url is None:
            return
        
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        job_name = f"transcription_job_{current_time}"
        language_code = "en-IN"  
        plain_transcript, words_times= Transcrib().start_transcription_job(job_name, s3_url, language_code)
        rule_list = Transcrib().list_rules(program_type=program_type)
        p1 = Transcrib().prompt_for_audio_rule(words_times, prompt_template_audio_duration)
        p1_response = Transcrib().generate_response(p1)
        print("TYPE_OF_RESPONSE-->", type(p1_response))
        print("P1_RESPONSE--->", p1_response)
        data = []
        try:
            p1_data = json.loads(p1_response)
            data.append({
                "Data1": [{"time": f"{p1_data.get('Time', 'x')} sec"}]
            })
        except Exception as e:
            print("Error parsing P1_response:", str(e))

        if rule_list is None:
            return {"data": data}
        else:
            rules_str = json.dumps(rule_list, indent=4)
            prompt = prompt_template_video_frame.format(rules=rules_str)
            
            p2 = Transcrib().prompt_for_audio_rule(plain_transcript, prompt)
            p2_response = Transcrib().generate_response(p2)
            try:
                if p2_response.strip()[0] != '[':
                    p2_response = f"[{p2_response}]"
            except Exception as e:
                print("Error-->", str(e))
            try:
                p2_data = json.loads(p2_response.replace('},', '},\n'))
                data.append({
                    "Data2": p2_data
                })
            except Exception as e:
                p2_data = []
            return  data