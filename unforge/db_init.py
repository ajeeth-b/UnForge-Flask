import boto3
from botocore.config import Config
from flask import current_app as app

my_config = Config(
    region_name = 'us-east-1'
)

dynamodb = boto3.resource(
	'dynamodb',
	aws_access_key_id = app.config['AWS_ACCESS_KEY_ID'], 
	aws_secret_access_key = app.config['AWS_SECRET_ACCESS_KEY'], 
	config=my_config
	)

data_table = dynamodb.Table('UnForge')
_save_space = app.config['SAVE_SPACE_IN_DYNAMO_DB']