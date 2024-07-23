import re
import os
from src.config.credentials import db_config,region_name, aws_access_key_id, aws_secret_access_key, S3_BUCKET
from src.config.queries import PROGRAM_ID, SELECT_RULES_BY_PROGRAM_VIDEO
from src.config.prompts import prompt_template_video_frame, prompt_template_audio_duration
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
        print("***************************************")
        print(response)
        return response


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
            cursor.execute(query)
            rules = cursor.fetchall()
            print("Rules-->", rules)
            if len(rules) == 0:
                return None
            else:
                dictionary = {item[0]: (item[1], item[2]) for item in rules}
                return dictionary           
        except Exception as e:
            return None


    @staticmethod
    def prompt_for_audio_rule(trancript,  prompt_template1 ):
            prompt = f"Trancript--->{trancript}\n INSTRUCTION-->{prompt_template1}"
            return prompt

    def process_audio_transcription(self, file, program_type):
        # s3_file = os.path.basename(file)
        # s3_url = Transcrib().upload_to_aws(file, s3_file)
        # if s3_url is None:
        #     return
        
        # # Define job details
        # current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        # job_name = f"transcription_job_{current_time}"
        # language_code = "en-IN"  # or any appropriate language code
        # plain_transcript, words_times= Transcrib().start_transcription_job(job_name, s3_url, language_code)
        print("Transcription Completed")
        print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWww")
        words_times = [('Hello', '0.009', '0.43'), ('This', '0.439', '0.72'), ('is', '0.73', '0.81'), ('Hardik', '0.819', '1.159'), ('Shah', '1.21', '1.289'), ('and', '1.74', '1.929'), ('today', '1.94', '2.309'), ('I', '2.319', '2.45'), ('am', '2.46', '2.539'), ('going', '2.549', '2.69'), ('to', '2.7', '2.75'), ('speak', '2.759', '3.049'), ('on', '3.059', '3.349'), ('a', '3.359', '3.369'), ('access', '3.5', '4.03'), ('corporate', '4.039', '4.44'), ('debt', '4.449', '4.69'), ('fund', '4.699', '5.07'), ("Let's", '5.86', '6.13'), ('understand', '6.139', '6.579'), ('what', '6.59', '6.719'), ('is', '6.73', '6.88'), ('Axis', '6.889', '7.13'), ('Corporate', '7.139', '7.539'), ('Debt', '7.55', '7.739'), ('Fund', '7.75', '8.14'), ('Axis', '8.76', '9.09'), ('Corporate', '9.1', '9.51'), ('Debt', '9.52', '9.72'), ('Fund', '9.729', '10.05'), ('is', '10.06', '10.35'), ('an', '10.359', '10.42'), ('open', '10.43', '10.819'), ('ended', '10.829', '11.229'), ('debt', '11.239', '11.43'), ('scheme', '11.439', '11.89'), ('predominantly', '11.899', '13.029'), ('investing', '13.039', '13.6'), ('in', '13.609', '13.689'), ('AA', '13.699', '14.01'), ('plus', '14.02', '14.399'), ('and', '14.409', '14.619'), ('above', '14.63', '14.97'), ('rated', '14.979', '15.289'), ('corporate', '15.3', '15.71'), ('bonds', '15.72', '16.329'), ('The', '17.04', '17.229'), ('fund', '17.239', '17.53'), ('has', '17.54', '17.75'), ('a', '17.76', '17.77'), ('relatively', '17.78', '18.399'), ('high', '18.409', '18.729'), ('interest', '18.739', '19.209'), ('rate', '19.219', '19.36'), ('risk', '19.37', '19.829'), ('and', '19.959', '20.28'), ('moderate', '20.29', '20.829'), ('credit', '20.84', '21.27'), ('risk', '21.28', '21.87'), ('As', '21.969', '22.309'), ('a', '22.319', '22.329'), ('category', '22.34', '23.11'), ('the', '23.329', '23.54'), ('fund', '23.549', '23.86'), ('needs', '23.87', '24.27'), ('to', '24.28', '24.469'), ('maintain', '24.479', '25.149'), ('minimum', '25.29', '25.87'), ('80%', '25.879', '26.59'), ('of', '26.6', '26.76'), ('its', '26.77', '26.93'), ('investments', '26.94', '27.819'), ('in', '27.829', '27.989'), ('AA', '28.0', '28.29'), ('plus', '28.299', '28.819'), ('and', '28.909', '29.19'), ('above', '29.2', '29.579'), ('rated', '29.59', '29.87'), ('corporate', '29.879', '30.329'), ('debt', '30.34', '30.78'), ('at', '30.79', '30.879'), ('all', '30.889', '31.149'), ('points', '31.159', '31.52'), ('It', '31.53', '31.549'), ('is', '31.559', '31.95'), ('an', '31.959', '32.069'), ('actively', '32.08', '32.68'), ('managed', '32.689', '33.0'), ('strategy', '33.009', '33.63'), ('Looks', '34.055', '34.435'), ('for', '34.444', '34.764'), ('opportunities', '34.775', '35.595'), ('across', '35.604', '36.205'), ('The', '36.775', '36.994'), ('scheme', '37.005', '37.595'), ('seeks', '37.604', '38.134'), ('to', '38.145', '38.244'), ('provide', '38.255', '38.965'), ('steady', '38.974', '39.575'), ('income', '39.584', '40.215'), ('and', '40.224', '40.654'), ('capital', '40.665', '41.294'), ('appreciation', '41.305', '42.014'), ('by', '42.115', '42.474'), ('predominantly', '42.485', '43.435'), ('investing', '43.444', '44.055'), ('in', '44.064', '44.174'), ('2', '44.185', '44.404'), ('to', '44.415', '44.525'), ('5', '44.534', '44.834'), ('year', '44.854', '45.185'), ('AAA', '45.194', '45.654'), ('corporate', '45.665', '46.125'), ('bonds', '46.134', '46.685'), ('So', '46.935', '47.224'), ('what', '47.235', '47.395'), ('is', '47.404', '47.494'), ('the', '47.505', '47.544'), ('current', '47.555', '47.875'), ('strategy', '47.884', '48.325'), ('of', '48.334', '48.474'), ('the', '48.485', '48.604'), ('fund', '48.615', '48.994'), ('In', '49.005', '49.084'), ('the', '49.095', '49.194'), ('current', '49.205', '49.715'), ('market', '49.724', '50.244'), ('environment', '50.255', '50.924'), ('Top', '51.5', '51.849'), ('down', '51.86', '52.15'), ('macro', '52.159', '52.569'), ('approach', '52.58', '53.36'), ('determines', '53.45', '54.15'), ('our', '54.159', '54.18'), ('investment', '54.189', '54.74'), ('strategy', '54.75', '55.2'), ('of', '55.209', '55.36'), ('the', '55.369', '55.479'), ('fund', '55.49', '56.0'), ('while', '56.299', '56.939'), ('core', '56.95', '57.34'), ('view', '57.349', '57.619'), ('guides', '57.63', '58.159'), ('the', '58.169', '58.31'), ('asset', '58.319', '58.68'), ('allocation', '58.689', '59.189'), ('of', '59.2', '59.279'), ('the', '59.29', '59.36'), ('fund', '59.369', '59.759'), ('In', '59.909', '60.02'), ('the', '60.029', '60.119'), ('current', '60.13', '60.5'), ('macro', '60.509', '60.819'), ('backdrop', '60.83', '61.83'), ('our', '61.84', '61.86'), ('core', '61.869', '62.299'), ('view', '62.31', '62.45'), ('continues', '62.459', '63.279'), ('to', '63.29', '63.4'), ('remain', '63.409', '63.84'), ('constructive', '63.849', '64.55'), ('on', '64.559', '64.739'), ('rates', '64.75', '65.22'), ('due', '65.33', '65.589'), ('to', '65.599', '65.73'), ('positive', '65.739', '66.199'), ('demand', '66.209', '66.599'), ('supply', '66.61', '66.9'), ('dynamics', '66.91', '67.529'), ('and', '67.65', '68.08'), ('favourable', '68.089', '68.68'), ('domestic', '68.69', '69.18'), ('macro', '69.19', '69.559'), ('environment', '69.589', '70.25'), ('for', '70.26', '70.459'), ('rates', '70.47', '70.959'), ('The', '70.97', '71.19'), ('current', '71.199', '71.58'), ('fixed', '71.589', '71.86'), ('income', '71.87', '72.16'), ('allocation', '72.269', '73.089'), ('in', '73.309', '73.629'), ('anticipation', '73.639', '74.519'), ('of', '74.529', '74.73'), ('FP', '74.739', '75.16'), ('a', '75.169', '75.18'), ('buying', '75.19', '75.889'), ('for', '76.019', '76.61'), ('JP', '76.62', '77.05'), ('Morgan', '77.059', '77.41'), ('index', '77.419', '77.83'), ('from', '77.839', '78.01'), ('next', '78.019', '78.33'), ('month', '78.339', '78.69'), ('is', '78.699', '78.97'), ('tilted', '78.98', '79.47'), ('towards', '79.48', '79.919'), ('long', '79.93', '80.47'), ('sovereign', '80.48', '81.199'), ('and', '81.209', '81.65'), ('high', '81.66', '81.97'), ('quality', '81.98', '82.569'), ('corporate', '82.58', '83.069'), ('bond', '83.08', '83.449'), ('investments', '83.459', '84.18'), ('Of', '84.19', '84.529'), ('the', '84.54', '84.65'), ('total', '84.66', '85.15'), ('allocation', '85.16', '85.709'), ('in', '85.72', '85.769'), ('corporate', '85.779', '86.18'), ('bonds', '86.19', '86.809'), ('majority', '86.83', '87.75'), ('is', '87.76', '87.97'), ('concentrated', '87.98', '88.949'), ('towards', '88.959', '89.309'), ('liquid', '89.319', '89.79'), ('PF', '89.8', '90.4'), ('banking', '90.66', '91.529'), ('and', '91.54', '91.91'), ('PSU', '91.919', '92.41'), ('bonds', '92.419', '92.93'), ('The', '93.889', '94.059'), ('investments', '94.069', '94.8'), ('are', '94.809', '95.05'), ('heavily', '95.059', '95.529'), ('concentrated', '95.54', '96.72'), ('in', '96.73', '96.849'), ('the', '96.86', '97.019'), ('2', '97.029', '97.25'), ('to', '97.26', '97.41'), ('5', '97.419', '97.76'), ('year', '97.769', '97.919'), ('duration', '97.93', '98.47'), ('assets', '98.48', '99.04'), ('which', '99.139', '99.489'), ('is', '99.5', '99.849'), ('in', '99.86', '99.94'), ('line', '99.949', '100.37'), ('with', '100.379', '100.529'), ('the', '100.54', '100.69'), ('fund', '100.699', '101.069'), ('strategy', '101.08', '101.86'), ('So', '102.29', '102.589'), ('in', '102.599', '102.69'), ('the', '102.699', '102.8'), ('current', '102.809', '103.099'), ('macro', '103.11', '103.43'), ('background', '103.44', '103.91'), ('why', '103.919', '104.26'), ('is', '104.269', '104.379'), ('it', '104.389', '104.41'), ('good', '104.419', '104.69'), ('for', '104.699', '104.809'), ('investors', '104.819', '105.61'), ('Prevailing', '106.309', '107.05'), ('domestic', '107.059', '107.709'), ('macro', '107.72', '108.069'), ('backdrop', '108.08', '108.79'), ('of', '108.8', '109.019'), ('falling', '109.029', '109.43'), ('CP', '109.44', '109.9'), ('I', '109.91', '110.059'), ('and', '110.19', '110.65'), ('strong', '110.66', '111.16'), ('external', '111.169', '111.69'), ('sector', '111.699', '112.29'), ('is', '112.5', '112.76'), ('favourable', '112.769', '113.449'), ('for', '113.459', '113.639'), ('rates', '113.65', '114.209'), ('and', '114.43', '114.69'), ('provides', '114.699', '115.199'), ('a', '115.209', '115.22'), ('good', '115.23', '115.69'), ('opportunity', '115.699', '116.29'), ('for', '116.3', '116.489'), ('investors', '116.5', '117.25'), ('to', '117.26', '117.41'), ('capture', '117.419', '117.91'), ('the', '117.919', '118.059'), ('high', '118.069', '118.529'), ('interest', '118.54', '119.04'), ('rates', '119.05', '119.309'), ('in', '119.319', '119.389'), ('the', '119.4', '119.489'), ('market', '119.5', '120.05'), ("Government's", '120.059', '120.66'), ('fiscal', '120.669', '121.11'), ('discipline', '121.12', '121.809'), ('followed', '121.819', '122.4'), ('by', '122.41', '122.55'), ('robust', '122.559', '123.029'), ('revenue', '123.04', '123.379'), ('collection', '123.389', '124.029'), ('provides', '124.04', '124.849'), ('adequate', '124.86', '125.36'), ('cushion', '125.37', '125.849'), ('to', '125.86', '126.129'), ('the', '126.139', '126.309'), ('borrowing', '126.319', '126.76'), ('programme', '126.769', '127.16'), ('of', '127.169', '127.3'), ('the', '127.309', '127.4'), ('government', '127.41', '127.93'), ('This', '128.929', '129.46'), ('coupled', '129.47', '129.96'), ('with', '129.97', '130.199'), ('index', '130.21', '130.71'), ('led', '130.72', '130.83'), ('FP', '130.839', '131.399'), ('a', '131.41', '131.419'), ('flows', '131.429', '132.179'), ('should', '132.19', '132.72'), ('be', '132.729', '132.929'), ('positive', '132.94', '133.619'), ('for', '133.63', '133.899'), ('bond', '133.91', '134.36'), ('yields', '134.369', '134.919'), ('Investors', '135.149', '135.86'), ('can', '135.869', '136.11'), ('use', '136.119', '136.699'), ('the', '136.71', '136.86'), ('current', '136.869', '137.259'), ('higher', '137.27', '137.69'), ('yields', '137.699', '138.22'), ('to', '138.33', '138.6'), ('build', '138.61', '139.119'), ('in', '139.13', '139.27'), ('duration', '139.279', '140.05'), ('What', '140.529', '140.789'), ('is', '140.8', '140.88'), ('the', '140.889', '140.919'), ('ideal', '140.929', '141.27'), ('investment', '141.279', '141.72'), ('horizon', '141.729', '142.279'), ('for', '142.289', '142.559'), ('investors', '142.57', '143.44'), ('The', '144.27', '144.49'), ('fund', '144.5', '144.88'), ('is', '144.889', '145.05'), ('suitable', '145.059', '145.69'), ('for', '145.699', '146.05'), ('investors', '146.059', '147.08'), ('who', '147.139', '147.399'), ('are', '147.41', '147.46'), ('looking', '147.47', '147.97'), ('at', '147.979', '148.139'), ('investing', '148.149', '148.929'), ('for', '148.94', '149.19'), ('a', '149.199', '149.21'), ('shorter', '149.22', '149.63'), ('duration', '149.639', '150.059'), ('product', '150.07', '150.69'), ('typically', '150.699', '151.339'), ('1', '151.35', '151.539'), ('to', '151.55', '151.669'), ('3', '151.679', '152.0'), ('year', '152.009', '152.07'), ('investment', '152.08', '152.649'), ('horizon', '152.66', '153.169'), ('which', '153.83', '154.16'), ('offers', '154.169', '154.72'), ('low', '154.729', '155.009'), ('volatility', '155.02', '155.86'), ('and', '156.119', '156.38'), ('can', '156.389', '156.699'), ('be', '156.71', '156.96'), ('substitute', '156.97', '157.66'), ('to', '157.669', '157.86'), ('traditional', '157.869', '158.679'), ('instruments', '158.69', '159.539'), ('while', '159.71', '160.22'), ('maintaining', '160.229', '160.75'), ('liquidity', '160.759', '161.5'), ('The', '161.679', '161.86'), ('fund', '161.869', '162.169'), ('offers', '162.179', '162.699'), ('ability', '162.71', '163.22'), ('to', '163.229', '163.35'), ('take', '163.36', '163.699'), ('advantage', '163.71', '164.46'), ('of', '164.47', '164.66'), ('the', '164.669', '164.82'), ('relatively', '164.83', '165.47'), ('high', '165.479', '165.82'), ('yields', '165.83', '166.339'), ('prevailing', '166.35', '167.179'), ('in', '167.19', '167.22'), ('the', '167.229', '167.339'), ('corporate', '167.35', '167.839'), ('debt', '167.85', '168.139'), ('instruments', '168.149', '168.979'), ('Mutual', '174.35', '174.839'), ('fund', '174.85', '175.08'), ('investments', '175.089', '175.699'), ('are', '175.71', '175.94'), ('subject', '175.949', '176.289'), ('to', '176.3', '176.369'), ('market', '176.38', '176.77'), ('risks', '176.779', '177.259'), ('Read', '177.27', '177.57'), ('all', '177.58', '177.72'), ('scheme', '177.729', '178.039'), ('related', '178.07', '178.36'), ('documents', '178.369', '178.91'), ('carefully', '178.919', '179.449')]
        rule_list = Transcrib().list_rules(program_type=program_type)
        print("final rule list---->", rule_list)

        p1 = Transcrib().prompt_for_audio_rule(words_times, prompt_template_audio_duration)

        p1_response = Transcrib().generate_response(p1)
        if rule_list is None:
            print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
            return p1_response, None
        else:
            print("++++++++++++++++++++++++++++++++++++=")
            rules_str = json.dumps(rule_list, indent=4)
            prompt = prompt_template_video_frame.format(rules=rules_str)

            p2 = Transcrib().prompt_for_audio_rule(plain_transcript, prompt)
            p2_response = Transcrib().generate_response(p2)
            return p1_response, p2_response
       