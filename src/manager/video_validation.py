import cv2
import numpy as np
import boto3
from PIL import Image
import pytesseract
from io import BytesIO
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from src.config.credentials import db_config, region_name, aws_access_key_id,aws_secret_access_key, S3_BUCKET
from src.config.queries import PROGRAM_ID, SELECT_RULES_BY_PROGRAM, SELECT_RULES_BY_PROGRAM_VIDEO
from src.config.prompts import prompt_template_video_frame
import os
import psycopg2
import imagehash
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")
    exit()


class VideoProcessor:
    def __init__(self, video_path, change_threshold=0.8, min_word_count=15):
        self.video_path = video_path
        self.s3_bucket_name = S3_BUCKET
        self.s3_folder = "frame-analysis"
        self.change_threshold = change_threshold
        self.min_word_count = min_word_count

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name= region_name
        )
        self.fps = None
        self.frame_count = None
        self.duration = None
    
    def get_video_properties(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video {self.video_path}.")
        
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps
        cap.release()
    
    def calculate_frame_differences(self):
        cap = cv2.VideoCapture(self.video_path)
        prev_frame = None
        frame_differences = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_frame is not None:
                diff = cv2.absdiff(prev_frame, gray)
                frame_differences.append(np.sum(diff))
            prev_frame = gray
        cap.release()
        frame_differences = np.array(frame_differences) / 1e6
        return frame_differences
    
    def find_stable_intervals(self, frame_differences):
        stable_intervals = []
        start_frame = 0

        for i, diff in enumerate(frame_differences):
            if diff > self.change_threshold:
                if start_frame < i - 1:
                    end_frame = i
                    start_time = start_frame / self.fps
                    end_time = end_frame / self.fps
                    stable_intervals.append((start_time, end_time))
                start_frame = i + 1

        if start_frame < len(frame_differences) - 1:
            end_time = len(frame_differences) / self.fps
            start_time = start_frame / self.fps
            stable_intervals.append((start_time, end_time))

        return stable_intervals

    def get_frame_number(self, second):
        return int(self.fps * second)
    
    def capture_frames(self, intervals):
        cap = cv2.VideoCapture(self.video_path)
        frame_counter = 1
        for start, end in intervals:
            end_frame = self.get_frame_number(end)
            cap.set(cv2.CAP_PROP_POS_FRAMES, end_frame)
            ret, frame = cap.read()
            if ret:
                filename = f'frame_{frame_counter}.png'  # Use the counter for the filename
                cv2.imwrite(filename, frame)
                self.upload_to_s3(filename)
                os.remove(filename)
                print(f"Saved frame {frame_counter} at {start:.2f} to {end:.2f} seconds as {filename}")
                frame_counter += 1  # Increment the counter after saving each frame
            else:
                print(f"Failed to capture frame at {start:.2f} to {end:.2f} seconds.")

        cap.release()

    def upload_to_s3(self, filename):
        with open(filename, "rb") as f:
            self.s3_client.upload_fileobj(f, self.s3_bucket_name, f"{self.s3_folder}/{filename}")

    def filter_frames(self):
        response = self.s3_client.list_objects_v2(Bucket=self.s3_bucket_name, Prefix=self.s3_folder)
        s3_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith(('jpg', 'jpeg', 'png'))]
        for s3_file in s3_files:
            s3_object = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=s3_file)
            img_data = s3_object['Body'].read()
            img = Image.open(BytesIO(img_data))
            extracted_text = pytesseract.image_to_string(img)
            word_count = len(extracted_text.split())
            if word_count < self.min_word_count:
                print(f"Insufficient text: Deleting frame {s3_file}.")
                self.s3_client.delete_object(Bucket=self.s3_bucket_name, Key=s3_file)

    def calculate_hash(self, image, hash_func=imagehash.average_hash):
        return hash_func(image)
    
    def delete_similar_images(self, hash_func=imagehash.average_hash, threshold=5):
        response = self.s3_client.list_objects_v2(Bucket=self.s3_bucket_name, Prefix=self.s3_folder)
        image_keys = [content['Key'] for content in response.get('Contents', []) if content['Key'].lower().endswith(('.png', '.jpg', '.jpeg'))]
        hashes = {}
        deleted_images = []

        for key in image_keys:
            try:
                response = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=key)
                img = Image.open(BytesIO(response['Body'].read()))
                img_hash = self.calculate_hash(img, hash_func)
            except Exception as e:
                logging.error(f"Error processing image {key}: {e}")
                continue

            to_delete = []
            for h, existing_key in hashes.items():
                if abs(img_hash - h) <= threshold:
                    to_delete.append(existing_key)

            for del_key in to_delete:
                try:
                    self.s3_client.delete_object(Bucket=self.s3_bucket_name, Key=del_key)
                    deleted_images.append(del_key)
                    logging.info(f'Deleted: {del_key}')
                    del hashes[h]  # Ensure to handle this correctly if deletion is not successful
                except Exception as e:
                    logging.error(f'Error deleting file {del_key}: {e}')

            if key not in deleted_images:
                hashes[img_hash] = key
        
  
    def process_video(self):
        try:
            self.get_video_properties()
            frame_differences = self.calculate_frame_differences()
            stable_intervals = self.find_stable_intervals(frame_differences)
            print("Done with time interval")
            self.capture_frames(stable_intervals)
            self.filter_frames()
            self.delete_similar_images()
            print("=================== Done with Image filteration =======================")
        except Exception as e:
            print(str(e))


class S3ImageProcessor:
    def __init__(self,program_type):
        self.program_type = program_type
        self.s3_bucket_name = S3_BUCKET
        self.s3_folder = "frame-analysis"
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.textract = boto3.client(
            'textract',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        self.system_prompt = "Answer the question from given content."
        self.max_tokens = 1000

    def list_s3_files(self):
        response = self.s3_client.list_objects_v2(Bucket=self.s3_bucket_name, Prefix=self.s3_folder)
        s3_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith(('jpg', 'jpeg', 'png'))]
        return s3_files
    
    def list_rules(self):
        try:    
            cursor.execute(PROGRAM_ID, (self.program_type,))
            program_id = cursor.fetchone()[0]  # Assuming the ID is the first column in the tuple
            cursor.execute(SELECT_RULES_BY_PROGRAM_VIDEO, (program_id, "Video",))
            rules = cursor.fetchall()

            print("##########################################")
            print("Rules-->", rules)
            dictionary = {item[0]: (item[1], item[2]) for item in rules}
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!",dictionary)
            return dictionary           
        except Exception as e:
            print(str(e))

    def extract_text_from_image(self, image_data):
        response = self.textract.detect_document_text(Document={'Bytes': image_data})
        text = ""
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                text += item["Text"] + "\n"
        return text

    def generate_message(self, messages):
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "system": self.system_prompt,
            "messages": messages
        })
        response = self.bedrock_runtime.invoke_model(body=body, modelId=self.model_id)
        response_body_str = response.get('body').read()
        response_body = json.loads(response_body_str)
        text_value = response_body['content'][0]['text']
        return text_value

    def generate_response(self, input_text):
        try:
            user_message = {"role": "user", "content": input_text}
            messages = [user_message]
            response_text = self.generate_message(messages)
            valid_json_string = '[' + response_text.strip().replace('}\n{', '},\n{') + ']'
            parsed_json = json.loads(valid_json_string)

            # if not response_text.strip():
            #     print("No response received.")
            #     return []

            # # Assuming response_text contains multiple JSON objects separated by newlines
            # json_objects = response_text.strip().split('\n')
            # parsed_responses = [json.loads(obj) for obj in json_objects if obj.strip()]
            return parsed_json

        except json.JSONDecodeError as jde:
            print("JSON Decode Error-->", jde)
            return None
        except Exception as err:
            print("ERROR-->", err)
            return None

    
    def process_images(self):
        s3_files = self.list_s3_files()
        print("List of S3 files-->", s3_files)
        rules = self.list_rules()
        rules_str = json.dumps(rules, indent=4)
        print("RULES--->", rules_str)
        try:
            prompt = prompt_template_video_frame.format(rules=rules_str)
        except Exception as e:
            print("Error-->",str(e))
        responses = {}
        try:
            for s3_file in s3_files:
                s3_object = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=s3_file)
                image_data = s3_object['Body'].read()
                text = self.extract_text_from_image(image_data)
                text = text + "\n" + prompt
                response = self.generate_response(text)
                s3_file = self.s3_bucket_name + '/' + s3_file
                responses[s3_file] = response
            return responses
        except Exception as e:
            print(str(e))




class Get_Image_url:
    
    def get_image_url(key: str):
        
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
            
            url = s3_client.generate_presigned_url(
                'getObject',
                Params={'Bucket': S3_BUCKET, 'Key': key},
                ExpiresIn=3600  # URL expiration time in seconds
            )
            return  url
        except (NoCredentialsError, PartialCredentialsError):
            return 0