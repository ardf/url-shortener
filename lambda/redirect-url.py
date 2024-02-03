import os
import json
import boto3
from boto3.dynamodb.conditions import Key
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)

ddb_table_name = os.environ.get("DDB_TABLE_NAME", "url-shortener")
ddb = boto3.resource("dynamodb", region_name="ap-south-1").Table(ddb_table_name)

default_error_url = os.environ.get("DEFAULT_ERROR_URL", "https://ardf.github.io/404")


def get_long_url(short_id):
    try:
        response = ddb.get_item(Key={"short_id": short_id})
        return response.get("Item", {}).get("long_url")
    except Exception as e:
        log.error(e)


def increment_hits(short_id):
    try:
        ddb.update_item(
            Key={"short_id": short_id},
            UpdateExpression="SET hits = hits + :val",
            ExpressionAttributeValues={":val": 1},
        )
    except Exception as e:
        log.error(e)


def generate_redirect_response(status_code, location):
    return {"statusCode": status_code, "headers": {"location": location}}


def lambda_handler(event, context):
    short_id = event["pathParameters"]["path_name"]
    try:
        long_url = get_long_url(short_id)
        if long_url:
            increment_hits(short_id)
        else:
            raise Exception("ID not found")

    except Exception as e:
        log.error(e)
        return generate_redirect_response(302, default_error_url)

    return generate_redirect_response(302, long_url)
