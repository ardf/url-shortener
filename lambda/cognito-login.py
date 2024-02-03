import json
import boto3
from botocore.exceptions import ClientError
import hmac
import hashlib
import base64
import os


def calculate_secret_hash(client_id, client_secret, username):
    message = username + client_id
    dig = hmac.new(
        str(client_secret).encode("utf-8"),
        msg=str(message).encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(dig).decode()


# Specify your Cognito user pool details
user_pool_id = os.environ.get("USER_POOL_ID")
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
cognito_client = boto3.client("cognito-idp")


def lambda_handler(event, context):
    # Extracting username and password from the API Gateway POST request body
    request_body = json.loads(event["body"])
    username = request_body.get("username")
    password = request_body.get("password")

    # Initializing Cognito client

    try:
        # Authenticating the user using the provided username and password
        response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
                "SECRET_HASH": calculate_secret_hash(
                    client_id, client_secret, username
                ),
            },
            ClientId=client_id,
        )

        # Extracting the authentication result
        authentication_result = response["AuthenticationResult"]

        # Constructing the response to be returned by the API Gateway
        api_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Authentication successful",
                    "AuthenticationResult": authentication_result,
                }
            ),
            "headers": {
                "Content-Type": "application/json",
            },
        }

        return api_response

    except ClientError as e:
        # If authentication fails, handle the error and return an appropriate response
        error_message = e.response["Error"]["Message"]
        api_response = {
            "statusCode": 401,
            "body": json.dumps(
                {"error": "Authentication failed", "message": error_message}
            ),
            "headers": {
                "Content-Type": "application/json",
            },
        }
        return api_response
