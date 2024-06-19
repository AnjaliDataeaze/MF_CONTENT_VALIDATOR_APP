import boto3
import json
import logging

from botocore.exceptions import ClientError
from src.config.credentials import aws_access_key_id, aws_secret_access_key, region_name


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DzBedrock:

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

            # Split the string by newline
            items = single_string.split('\n')

            formatted_response = {}
            # Iterating through each item in split_response and extracting key-value pairs
            for item in items:
                if ':' in item:
                    # Splitting each item by colon
                    key, value = item.split(':', 1)  # Limit split to 1 to avoid issues with extra colons
                    # Removing leading and trailing whitespaces from key and value
                    key = key.strip()
                    value = value.strip()
                    # Storing key-value pair in formatted_response dictionary
                    formatted_response[key] = value
                else:
                    print(f"Skipping item as it does not contain ':': {item}")

            return formatted_response
            # return response
        
        except ClientError as err:
            message=err.response["Error"]["Message"]
            logger.error("A client error occurred: %s", message)
            print("A client error occured: " +
                format(message))
            return None