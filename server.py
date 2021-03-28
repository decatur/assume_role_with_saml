import json
import pathlib
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from pprint import pprint

import boto3

sts = boto3.client('sts')


def assume_role_with_saml(saml_response: str, role_arn: str, principal_name: str) -> Path:
    m = re.search(r'(\d+)', role_arn)
    account = m.group(0)

    response = sts.assume_role_with_saml(
        RoleArn=role_arn,
        PrincipalArn='arn:aws:iam::{account}:saml-provider/{PrincipalName}'.format(
            account=account, PrincipalName=principal_name
        ),
        SAMLAssertion=saml_response,
        DurationSeconds=3600 * 12
    )
    pprint(response)
    credentials = response['Credentials']
    target_dir = (pathlib.Path.home() / '.aws' / 'credentials')
    target_dir.write_text("\n".join([
        '[default]',
        'aws_access_key_id=' + credentials['AccessKeyId'],
        'aws_secret_access_key=' + credentials['SecretAccessKey'],
        'aws_session_token=' + credentials['SessionToken']]))

    return target_dir


class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    principal_name: str

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        request_body = self.rfile.read(content_length).decode('utf-8')
        print(request_body)
        request_dict = json.loads(request_body)
        pprint(request_dict)
        if self.path == '/saml':
            status = 200
            try:
                target_dir = assume_role_with_saml(
                    request_dict['SAMLResponse'], request_dict['roleARN'], self.principal_name
                )
                body = {'target_dir': str(target_dir)}
            except Exception as e:
                status = 400
                body = {'error': str(e)}

            self.send_response(status)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(body), encoding='utf8'))
        else:
            self.send_error(404, self.path)


def run(identity_provider_name: str):
    server_address = ('127.0.0.1', 9123)
    print(f'Starting assume_role_with_saml at {server_address}.\nWaiting for web client extension requests ...')
    MyHttpRequestHandler.principal_name = identity_provider_name
    httpd = HTTPServer(server_address, MyHttpRequestHandler)
    httpd.serve_forever()
