import json
import os
import logging
import boto3
from profiler import profile


logger = logging.getLogger()
logger.setLevel(logging.INFO)


lambda_client = boto3.client("lambda")


@profile
def lambda_handler(event, context):
    """
    Checks the incoming event and invokes the right handler
    """
    logger.debug(f"Incoming event: {event}")
    payload = json.loads(event['body'])
    # payload = event['body']
    try:
        if 'user' not in payload or "auth_id" not in payload['user']:
            raise Exception("Haven't received user details in payload")
        auth_params = payload['user']['auth_id'].split("_")
        source = auth_params[2] if len(auth_params) == 5 else auth_params[1]
        if source.lower() == "slack":
            data = {
                "client_id": auth_params[4],
                "itsm": auth_params[3],
                "user": auth_params[0] + "_" + auth_params[1],
                "body": payload
            }
            logger.info("Triggering Slack outbound handler")
            lambda_arn = os.environ.get("slack_outbound_handler_arn")
        elif source.lower() == "teams":
            data = {
                "client_id": auth_params[3],
                "itsm": auth_params[2],
                "user": auth_params[0],
                "body": payload
            }
            logger.info("Triggering teams outbound handler")
            lambda_arn = os.environ.get("teams_outbound_handler_arn")
        elif source.lower() == "zoom":
            data = {
                "client_id": auth_params[3],
                "itsm": auth_params[2],
                "user": auth_params[0],
                "body": payload
            }
            logger.info("Triggering zoom outbound handler")
            lambda_arn = os.environ.get("zoom_outbound_handler_arn")
        else:
            raise Exception(f"Invalid source returned by haptik: {source}")
    
        lambda_client.invoke(FunctionName=lambda_arn,
                             InvocationType="Event",
                             Payload=json.dumps(data))
            
    except Exception as e:
        logger.error(f"Encountered an exception while handling incoming Haptik events: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
