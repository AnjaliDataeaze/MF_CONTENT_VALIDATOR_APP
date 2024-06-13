import boto3
import time
import datetime
import json
import urllib.request
import re
from botocore.exceptions import NoCredentialsError
import os
from src.config.credentials import region_name, aws_access_key_id, aws_secret_access_key

# Function to upload a local file to AWS S3
class Transcrib:
 
    @staticmethod
    def upload_to_aws(local_file, bucket, s3_file):
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
           
        try:
            s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")

            return f"s3://{bucket}/{s3_file}"
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
            MediaFormat='mp3',  # or 'mp4', 'wav', 'flac'
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

            return transcription_result


    # Function to find the start and end timestamps of the last 14 words
    @staticmethod
    def find_statement_duration(transcription_result, word_count):
        items = [item for item in transcription_result['results']['items'] if item['type'] == 'pronunciation']
        if len(items) < word_count:
            return None

        start_time = float(items[-word_count]['start_time'])
        end_time = float(items[-1]['end_time'])

        return start_time, end_time, end_time - start_time

    def duration(self,local_file):
        bucket = 'mutual-fund-dataeaze'
        s3_file = os.path.basename(local_file)
        # Upload local file to S3 and get the S3 URL
        transcription = Transcrib()
        s3_url = transcription.upload_to_aws(local_file, bucket, s3_file)
        if s3_url is None:
            return

        # Define job details
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        job_name = f"transcription_job_{current_time}"
        language_code = "en-IN"  # or any appropriate language code

        # Start transcription job
        transcription_result = transcription.start_transcription_job(job_name, s3_url, language_code)
        if transcription_result is None:
            return

        # Find the statement duration
        word_count = 14
        result = transcription.find_statement_duration(transcription_result, word_count)

        if result:
            start_time, end_time, duration = result
            print(f"The statement starts at {start_time} seconds and ends at {end_time} seconds.")
            print(f"The duration of the statement is {duration} seconds.")
            return 1, duration
        else:
            print("The statement was not found in the transcription.")
            return 2, f"transcription not found"

    # if __name__ == "__main__":
    #     main()
