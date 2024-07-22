import re
import os
from src.config.credentials import db_config,region_name, aws_access_key_id, aws_secret_access_key, S3_BUCKET
from src.config.queries import PROGRAM_ID, SELECT_RULES_BY_PROGRAM_VIDEO
from src.config.prompts import prompt_template_audio
from botocore.exceptions import NoCredentialsError
import boto3
import time
import datetime
import json
import urllib.request
import psycopg2


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
        print("JobUri-->", job_uri)
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
        print(f"The job UIR is : {job_uri}")
        print(f"Started transcription job: {job_name}")

        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print("Not ready yet...")
            time.sleep(10)

        print(f"Transcription job status: {status['TranscriptionJob']['TranscriptionJobStatus']}")

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

    # # Function to clean text
    # def clean_text(text):
    #     # Remove punctuation and convert to lowercase
    #     return re.sub(r'[^\w\s]', '', text).lower()

    # # Function to find the start and end timestamps of the last 14 words
    # def find_statement_duration(transcription_result, word_count):
    #     items = [item for item in transcription_result['results']['items'] if item['type'] == 'pronunciation']
    #     if len(items) < word_count:
    #         return None

    #     start_time = float(items[-word_count]['start_time'])
    #     end_time = float(items[-1]['end_time'])

    #     return start_time, end_time, end_time - start_time

    # @staticmethod
    # def prompt_to_find_of_disclaimer(transcript):
    #         instruction =f"""The provide text is audio transcription of mutual fund .
    #                         This text is in from of json, which contains the word and there there start time and endtime.
    #                         Your Task is to find out the total time in second of particular sentence .
    #                         Sentence is : 'Mutual Fund investments are subject to market risks, read all scheme related documents carefully.'
    #                         Response should be in given structure : Time of disclaimer = x sec"""
                        

    #         prompt = f"{transcript}\n{instruction}"
    #         return prompt
    
    @staticmethod
    def prompt_for_audio_rule(plain_transcript, word_time_transcript):
            prompt = f"PLAIN_TRANSCRIPT-->{plain_transcript}\n WORD_TIME --> {word_time_transcript}\n INSTRUCTION-->{prompt_template_audio}"
            return prompt
    
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
            try:
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
                single_string = response  
                return single_string
            
            except Exception as err:
                print(err)

    @staticmethod
    def list_rules(program_type):
        try:    
            cursor.execute(PROGRAM_ID, (program_type,))
            program_id_result = cursor.fetchone()
            program_id = program_id_result[0] 
            print("Program_id-->", program_id)
            query = f"""SELECT r.id, r.rulename, r.disclaimer
                      FROM rules r
                      JOIN rule_to_program rp ON r.id = rp.rules_id
                      WHERE rp.program_id = {program_id} AND r.media_type = 'audio' """
            # cursor.execute(SELECT_RULES_BY_PROGRAM_VIDEO, (program_id, "audio",))
            cursor.execute(query)
            rules = cursor.fetchall()
            dictionary = {item[0]: (item[1], item[2]) for item in rules}
            return dictionary           
        except Exception as e:
            print(str(e))

    def process_audio_transcription(self, file, program_type):
        s3_file = os.path.basename(file)
        s3_url = Transcrib().upload_to_aws(file, s3_file)
        if s3_url is None:
            return
        
        # Define job details
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        job_name = f"transcription_job_{current_time}"
        language_code = "en-IN"  # or any appropriate language code
        plan_transcript, word_time = Transcrib().start_transcription_job(job_name, s3_url, language_code)
        rule_list = Transcrib().list_rules(program_type=program_type)
        # return rule_list
        ## flow for 5 sec disclaimer
        p1 = Transcrib().prompt_for_audio_rule(plan_transcript, word_time)
        p1_response = Transcrib().generate_response(p1)
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(p1_response)
        return p1_response
        # p2 = Transcrib().
        # # Find the statement duration
        # word_count = 14
        # result = find_statement_duration(transcription_result, word_count)

        # if result:
        #     start_time, end_time, duration = result
        #     print(f"The statement starts at {start_time} seconds and ends at {end_time} seconds.")
        #     print(f"The duration of the statement is {duration} seconds.")
        # else:
        #     print("The statement was not found in the transcription.")

    # if __name__ == "__main__":
    #     main()
