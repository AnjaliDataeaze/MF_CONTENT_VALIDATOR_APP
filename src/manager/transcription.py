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
            print("++++++++++++called list rule function+++++++++++++++++")
            cursor.execute(PROGRAM_ID, (program_type,))
            program_id_result = cursor.fetchone()
            program_id = program_id_result[0] 
            cursor.execute(SELECT_RULES_BY_PROGRAM_AUDIO, (program_id,))
            rules = cursor.fetchall()
            print("LIST of RULES-->", rules)
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
        # s3_file = os.path.basename(file)
        # s3_url = Transcrib().upload_to_aws(file, s3_file)
        # if s3_url is None:
        #     return
        # print("Uploaded on s3")
        # current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        # job_name = f"transcription_job_{current_time}"
        # language_code = "en-IN"  
        # plain_transcript, words_times= Transcrib().start_transcription_job(job_name, s3_url, language_code)
        # print("===================================================")
        # print("PlAIN_ TRANCRIPT--->", plain_transcript)
        plain_transcript=" ever feel lost With stock markets, ups and downs, you're not alone. Market swings, influenced by everything from company news to global events, often make us buy high and sell low, which is not the best strategy for our investments. In such a scenario, How should one invest mate the Access Balance Advantage Fund? This fund smartly mixes investments between equity for growth and fixed income for diversification, adjusting from 0% 200% based on market conditions. This ensures your investments work hard even in unpredictable markets. How does the fund work? The Access Balance Advantage Fund operates through a three step process. Dynamic asset allocation, monthly review by Asset Allocation Committee and proactive decision making. The fund follows a five factor approach to determine equity exposure while rebalancing. All five variables are given importance while computing the net long exposure. Broad parameters like flows, geopolitical scenario and unexpected market events are also taken into consideration, ensuring a 360 degree coverage in black swan events such as Covid or Russia Ukraine War. The Asset Allocation Committee is equipped to immediately take active calls on asset allocation. Let's under understand the equity and debt asset allocation in detail. The equity allocation of the fund follows a flexi cap approach which focuses on absolute returns and risk reward relativity while offering growth and quality at a reasonable price. The fund has a cyclical approach over low growth and dynamically allocates assets based on different market conditions. The debt allocation of the fund comprises of high quality corporate bonds and G SE, which are mostly AAA rated bonds and follows a duration management between 1 to 7 years. Why should we consider the Access Balance Advantage Fund? This fund could be an ideal choice for those seeking to navigate market volatility intelligently. It offers dynamic decision making, eliminates the need for market timing and protect downside by reducing drawdowns all while potentially benefiting from equity taxation. Ready to grow your wealth regardless of market conditions. Learn more about how this fund can be a part of your financial strategy. Mutual fund investments are subject to market risks. Read all scheme related documents carefully"
        # print("WORDS_TIMESRCIPT--->", words_times)

        words_times = """[('ever', '0.009', '0.389'), ('feel', '0.4', '0.73'), ('lost', '0.74', '0.949'), ('With', '0.959', '1.169'), ('stock', '1.179', '1.5'), ('markets', '1.509', '1.97'), ('ups', '1.98', '2.16'), ('and', '2.17', '2.299'), ('downs', '2.309', '2.799'), ("you're", '2.9', '3.23'), ('not', '3.24', '3.41'), ('alone', '3.42', '3.91'), ('Market', '4.079', '4.599'), ('swings', '4.61', '5.059'), ('influenced', '5.07', '5.659'), ('by', '5.67', '5.869'), ('everything', '5.88', '6.55'), ('from', '6.559', '6.84'), ('company', '6.849', '7.199'), ('news', '7.21', '7.78'), ('to', '7.789', '7.98'), ('global', '7.989', '8.329'), ('events', '8.34', '8.81'), ('often', '8.88', '9.34'), ('make', '9.35', '9.609'), ('us', '9.619', '9.729'), ('buy', '9.739', '10.0'), ('high', '10.01', '10.5'), ('and', '10.539', '10.829'), ('sell', '10.84', '11.21'), ('low', '11.22', '11.47'), ('which', '11.479', '11.829'), ('is', '11.84', '11.949'), ('not', '11.96', '12.229'), ('the', '12.239', '12.35'), ('best', '12.359', '12.579'), ('strategy', '12.59', '13.199'), ('for', '13.21', '13.539'), ('our', '13.55', '13.63'), ('investments', '13.64', '14.439'), ('In', '14.729', '14.869'), ('such', '14.88', '15.17'), ('a', '15.18', '15.189'), ('scenario', '15.199', '15.869'), ('How', '15.88', '16.19'), ('should', '16.2', '16.469'), ('one', '16.479', '16.639'), ('invest', '16.649', '17.329'), ('mate', '17.659', '18.19'), ('the', '18.2', '18.469'), ('Access', '18.479', '18.889'), ('Balance', '18.899', '19.329'), ('Advantage', '19.34', '19.87'), ('Fund', '19.879', '20.19'), ('This', '20.45', '20.709'), ('fund', '20.719', '21.149'), ('smartly', '21.159', '21.77'), ('mixes', '21.78', '22.25'), ('investments', '22.26', '22.959'), ('between', '22.969', '23.329'), ('equity', '23.34', '23.85'), ('for', '23.86', '24.0'), ('growth', '24.01', '24.61'), ('and', '24.62', '24.79'), ('fixed', '24.799', '25.11'), ('income', '25.12', '25.549'), ('for', '25.559', '25.7'), ('diversification', '25.709', '26.79'), ('adjusting', '26.95', '27.629'), ('from', '27.639', '28.1'), ('0%', '28.2', '29.19'), ('200%', '29.2', '30.35'), ('based', '30.399', '30.909'), ('on', '30.92', '31.03'), ('market', '31.04', '31.36'), ('conditions', '31.37', '32.069'), ('This', '32.36', '32.689'), ('ensures', '32.7', '33.29'), ('your', '33.299', '33.54'), ('investments', '33.549', '34.159'), ('work', '34.169', '34.45'), ('hard', '34.459', '34.939'), ('even', '34.95', '35.43'), ('in', '35.439', '35.61'), ('unpredictable', '35.619', '36.369'), ('markets', '36.38', '37.009'), ('How', '37.15', '37.47'), ('does', '37.479', '37.72'), ('the', '37.729', '37.81'), ('fund', '37.819', '38.169'), ('work', '38.18', '38.63'), ('The', '38.639', '38.81'), ('Access', '38.819', '39.229'), ('Balance', '39.24', '39.68'), ('Advantage', '39.689', '40.25'), ('Fund', '40.259', '40.619'), ('operates', '40.63', '41.189'), ('through', '41.2', '41.479'), ('a', '41.49', '41.5'), ('three', '41.509', '41.84'), ('step', '41.849', '42.09'), ('process', '42.099', '42.97'), ('Dynamic', '42.979', '43.59'), ('asset', '43.599', '43.889'), ('allocation', '43.9', '44.549'), ('monthly', '44.56', '45.08'), ('review', '45.09', '45.419'), ('by', '45.43', '45.68'), ('Asset', '45.689', '46.09'), ('Allocation', '46.099', '46.63'), ('Committee', '46.639', '47.27'), ('and', '47.45', '47.72'), ('proactive', '47.729', '48.279'), ('decision', '48.29', '48.709'), ('making', '48.72', '49.25'), ('The', '49.459', '49.65'), ('fund', '49.659', '49.939'), ('follows', '49.95', '50.419'), ('a', '50.43', '50.439'), ('five', '50.45', '50.759'), ('factor', '50.77', '51.169'), ('approach', '51.18', '51.65'), ('to', '51.659', '51.9'), ('determine', '51.909', '52.49'), ('equity', '52.5', '52.93'), ('exposure', '52.939', '53.61'), ('while', '53.619', '54.009'), ('rebalancing', '54.02', '54.77'), ('All', '55.279', '55.58'), ('five', '55.59', '55.86'), ('variables', '55.869', '56.459'), ('are', '56.47', '56.72'), ('given', '56.729', '56.99'), ('importance', '57.0', '57.729'), ('while', '57.74', '58.069'), ('computing', '58.08', '58.63'), ('the', '58.639', '58.729'), ('net', '58.74', '59.029'), ('long', '59.04', '59.229'), ('exposure', '59.24', '59.959'), ('Broad', '59.97', '60.47'), ('parameters', '60.479', '61.169'), ('like', '61.18', '61.509'), ('flows', '61.52', '62.7'), ('geopolitical', '62.709', '63.509'), ('scenario', '63.52', '64.11'), ('and', '64.209', '64.51'), ('unexpected', '64.519', '65.169'), ('market', '65.18', '65.55'), ('events', '65.559', '66.04'), ('are', '66.069', '66.389'), ('also', '66.4', '66.68'), ('taken', '66.69', '67.069'), ('into', '67.08', '67.309'), ('consideration', '67.319', '68.269'), ('ensuring', '68.279', '69.029'), ('a', '69.04', '69.05'), ('360', '69.059', '69.709'), ('degree', '69.72', '70.069'), ('coverage', '70.08', '70.709'), ('in', '70.97', '71.129'), ('black', '71.139', '71.459'), ('swan', '71.47', '71.72'), ('events', '71.73', '72.089'), ('such', '72.099', '72.269'), ('as', '72.279', '72.48'), ('Covid', '72.489', '73.12'), ('or', '73.129', '73.29'), ('Russia', '73.3', '73.72'), ('Ukraine', '73.73', '74.139'), ('War', '74.15', '74.51'), ('The', '74.669', '74.86'), ('Asset', '74.87', '75.239'), ('Allocation', '75.25', '75.75'), ('Committee', '75.76', '76.199'), ('is', '76.209', '76.41'), ('equipped', '76.419', '76.79'), ('to', '76.8', '76.949'), ('immediately', '76.959', '77.519'), ('take', '77.529', '77.839'), ('active', '77.849', '78.269'), ('calls', '78.279', '78.769'), ('on', '78.779', '79.04'), ('asset', '79.05', '79.4'), ('allocation', '79.41', '80.069'), ("Let's", '80.26', '80.519'), ('under', '80.529', '80.699'), ('understand', '80.786', '81.106'), ('the', '81.115', '81.206'), ('equity', '81.216', '81.846'), ('and', '81.935', '82.265'), ('debt', '82.276', '82.466'), ('asset', '82.475', '82.846'), ('allocation', '82.856', '83.685'), ('in', '83.695', '83.725'), ('detail', '83.736', '84.286'), ('The', '84.426', '84.606'), ('equity', '84.615', '85.136'), ('allocation', '85.146', '85.765'), ('of', '85.776', '86.005'), ('the', '86.015', '86.125'), ('fund', '86.136', '86.536'), ('follows', '86.545', '86.996'), ('a', '87.005', '87.015'), ('flexi', '87.026', '87.346'), ('cap', '87.555', '87.706'), ('approach', '87.716', '88.246'), ('which', '88.335', '88.655'), ('focuses', '88.666', '89.136'), ('on', '89.146', '89.405'), ('absolute', '89.416', '89.926'), ('returns', '89.935', '90.625'), ('and', '90.636', '90.875'), ('risk', '90.886', '91.106'), ('reward', '91.115', '91.505'), ('relativity', '91.515', '92.316'), ('while', '92.325', '92.666'), ('offering', '92.676', '93.136'), ('growth', '93.146', '93.666'), ('and', '93.676', '93.816'), ('quality', '93.825', '94.486'), ('at', '94.566', '94.786'), ('a', '94.795', '94.805'), ('reasonable', '94.816', '95.365'), ('price', '95.375', '95.846'), ('The', '95.956', '96.155'), ('fund', '96.166', '96.606'), ('has', '96.615', '96.956'), ('a', '96.966', '96.975'), ('cyclical', '96.986', '97.496'), ('approach', '97.505', '97.835'), ('over', '97.846', '98.125'), ('low', '98.136', '98.265'), ('growth', '98.276', '98.725'), ('and', '98.886', '99.246'), ('dynamically', '99.255', '99.856'), ('allocates', '99.865', '100.295'), ('assets', '100.305', '100.896'), ('based', '100.905', '101.405'), ('on', '101.416', '101.536'), ('different', '101.545', '101.875'), ('market', '101.886', '102.176'), ('conditions', '102.185', '102.986'), ('The', '103.106', '103.316'), ('debt', '103.325', '103.606'), ('allocation', '103.615', '104.166'), ('of', '104.176', '104.286'), ('the', '104.295', '104.405'), ('fund', '104.416', '104.825'), ('comprises', '104.835', '105.526'), ('of', '105.536', '105.765'), ('high', '105.776', '105.996'), ('quality', '106.005', '106.255'), ('corporate', '106.512', '106.952'), ('bonds', '106.961', '107.501'), ('and', '107.522', '107.772'), ('G', '107.781', '107.961'), ('SE', '108.132', '108.302'), ('which', '108.311', '108.541'), ('are', '108.552', '108.652'), ('mostly', '108.662', '109.132'), ('AAA', '109.141', '109.741'), ('rated', '109.751', '110.141'), ('bonds', '110.152', '110.662'), ('and', '110.781', '111.031'), ('follows', '111.041', '111.452'), ('a', '111.461', '111.472'), ('duration', '111.482', '112.041'), ('management', '112.052', '112.592'), ('between', '112.601', '113.001'), ('1', '113.012', '113.202'), ('to', '113.211', '113.321'), ('7', '113.332', '113.641'), ('years', '113.652', '114.101'), ('Why', '114.111', '114.421'), ('should', '114.431', '114.662'), ('we', '114.671', '114.802'), ('consider', '114.811', '115.501'), ('the', '115.512', '115.702'), ('Access', '115.711', '116.122'), ('Balance', '116.132', '116.582'), ('Advantage', '116.592', '117.132'), ('Fund', '117.141', '117.482'), ('This', '117.491', '117.861'), ('fund', '117.872', '118.152'), ('could', '118.162', '118.342'), ('be', '118.351', '118.472'), ('an', '118.482', '118.582'), ('ideal', '118.592', '118.931'), ('choice', '118.942', '119.262'), ('for', '119.272', '119.391'), ('those', '119.402', '119.821'), ('seeking', '119.832', '120.262'), ('to', '120.272', '120.382'), ('navigate', '120.391', '120.942'), ('market', '120.952', '121.302'), ('volatility', '121.311', '122.152'), ('intelligently', '122.162', '123.202'), ('It', '123.311', '123.522'), ('offers', '123.531', '124.141'), ('dynamic', '124.152', '124.781'), ('decision', '124.791', '125.192'), ('making', '125.202', '125.772'), ('eliminates', '125.912', '126.711'), ('the', '126.722', '126.861'), ('need', '126.872', '127.262'), ('for', '127.272', '127.421'), ('market', '127.431', '127.732'), ('timing', '127.741', '128.341'), ('and', '128.552', '129.052'), ('protect', '129.072', '129.621'), ('downside', '129.632', '130.261'), ('by', '130.272', '130.462'), ('reducing', '130.472', '131.022'), ('drawdowns', '131.031', '131.772'), ('all', '132.119', '132.46'), ('while', '132.47', '132.699'), ('potentially', '132.71', '133.279'), ('benefiting', '133.289', '133.979'), ('from', '133.99', '134.35'), ('equity', '134.36', '134.75'), ('taxation', '134.759', '135.57'), ('Ready', '135.639', '136.059'), ('to', '136.07', '136.179'), ('grow', '136.19', '136.38'), ('your', '136.389', '136.589'), ('wealth', '136.6', '136.979'), ('regardless', '136.99', '137.58'), ('of', '137.589', '137.699'), ('market', '137.71', '137.99'), ('conditions', '138.0', '138.839'), ('Learn', '139.11', '139.509'), ('more', '139.52', '139.77'), ('about', '139.779', '140.22'), ('how', '140.229', '140.559'), ('this', '140.57', '140.74'), ('fund', '140.75', '140.99'), ('can', '141.0', '141.179'), ('be', '141.19', '141.35'), ('a', '141.36', '141.369'), ('part', '141.38', '141.699'), ('of', '141.71', '141.809'), ('your', '141.82', '141.979'), ('financial', '141.99', '142.52'), ('strategy', '142.529', '143.139'), ('Mutual', '145.309', '145.82'), ('fund', '145.83', '146.05'), ('investments', '146.059', '146.61'), ('are', '146.619', '146.82'), ('subject', '146.83', '147.179'), ('to', '147.19', '147.3'), ('market', '147.309', '147.619'), ('risks', '147.63', '148.199'), ('Read', '148.21', '148.539'), ('all', '148.55', '148.82'), ('scheme', '148.83', '149.169'), ('related', '149.179', '149.57'), ('documents', '149.58', '150.039'), ('carefully', '150.05', '150.66')]"""
        print("============calling direct =====================================")

        rule_list = Transcrib().list_rules(program_type=program_type)

        p1 = Transcrib().prompt_for_audio_rule(words_times, prompt_template_audio_duration)

        p1_response = Transcrib().generate_response(p1)
        print("P1_response-->", p1_response)
        print("TYPE_response-->", type(p1_response))
        cleaned_response = p1_response.replace("{", "").replace("}", "")

    
        data = []
    
        data.append({"Data1":cleaned_response})
        if rule_list is None:
            if len(data)==0:
                return  None
            else:
                print("Final Data --->", data)
                return  data
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
                pass

            if len(data)==0:
                return  None
            else:
                print("Final Data --->", data)
                return  data