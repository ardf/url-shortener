import os
import json
import boto3
from boto3.dynamodb.conditions import Key
from string import ascii_letters, digits
from random import choice, randint
from time import strftime, time
from urllib import parse
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)

APP_URL = os.environ.get("APP_URL")
MIN_LENGTH = os.environ.get("MIN_LENGTH", 7)
MAX_LENGTH = os.environ.get("MAX_LENGTH", 16)
MAX_ATTEMPTS_FOR_GENERATE_ID = os.environ.get("MAX_ATTEMPTS_FOR_GENERATE_ID", 5)


ID_FORMAT = ascii_letters + digits

ddb_table_name = os.environ.get("DDB_TABLE_NAME", "url-shortener")
ddb = boto3.resource("dynamodb", region_name="ap-south-1").Table(ddb_table_name)


def generate_timestamp():
    timestamp = strftime("%Y-%m-%dT%H:%M:%S")
    return timestamp


def get_expiry_date():
    expires_at = int(time()) + int(604800)
    return expires_at


def is_id_unique(short_id):
    response = ddb.get_item(Key={"short_id": short_id})
    if response.get("Item"):
        return False
    else:
        return True


def generate_id(attempt=1):
    if attempt > MAX_ATTEMPTS_FOR_GENERATE_ID:
        raise ValueError("Failed to generate a unique ID after multiple attempts.")
    short_id = "".join(
        choice(ID_FORMAT) for _ in range(randint(MIN_LENGTH, MAX_LENGTH))
    )
    if is_id_unique(short_id):
        return short_id
    else:
        return generate_id(attempt + 1)


def lambda_handler(event, context):
    request_body = json.loads(event.get("body"))
    try:
        username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    except KeyError:
        username = "anon"

    analytics = {}
    try:
        short_id = request_body.get("custom_short_id", None)
        if username != "anon" and short_id:
            if not is_id_unique(short_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps(
                        {
                            "error": "The Short ID is already in use. Please try another ID."
                        }
                    ),
                }
        else:
            short_id = generate_id()
    except Exception as e:
        log.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Something went wrong"}),
        }
    short_url = APP_URL + short_id
    long_url = request_body.get("long_url")
    timestamp = generate_timestamp()
    ttl_value = get_expiry_date()

    headers = event.get("headers")
    analytics["user_agent"] = headers.get("User-Agent")
    analytics["source_ip"] = headers.get("X-Forwarded-For")
    analytics["xray_trace_id"] = headers.get("X-Amzn-Trace-Id")

    query = parse.urlsplit(long_url).query
    if len(query) > 0:
        url_params = dict(parse.parse_qsl(parse.urlsplit(long_url).query))
        analytics.update(url_params)

    try:
        response = ddb.put_item(
            Item={
                "short_id": short_id,
                "created_at": timestamp,
                "expires_at": int(ttl_value),
                "short_url": short_url,
                "user_id": username,
                "long_url": long_url,
                "analytics": analytics,
                "hits": int(0),
            }
        )
    except Exception as e:
        log.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Something went wrong"}),
        }

    return {"statusCode": 200, "body": json.dumps({"short_url": short_url})}
