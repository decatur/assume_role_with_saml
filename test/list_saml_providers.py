import boto3, pprint
pprint.pprint(boto3.client('iam').list_saml_providers())
