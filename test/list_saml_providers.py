import boto3
import pprint

iam = boto3.client('iam')
response = iam.list_saml_providers()
pprint.pprint(response)