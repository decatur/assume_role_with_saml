import json
import pathlib
import re
from configparser import ConfigParser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from pprint import pprint

import boto3

sts = boto3.client('sts')
httpd: HTTPServer = None
accounts_by_number = {}


def assume_role_with_saml(saml_response: str, role_arn: str, principal_name: str) -> Path:
    account_number = re.search(r'(\d+)', role_arn).group(0)

    response = sts.assume_role_with_saml(
        RoleArn=role_arn,
        PrincipalArn='arn:aws:iam::{account}:saml-provider/{PrincipalName}'.format(
            account=account_number, PrincipalName=principal_name
        ),
        SAMLAssertion=saml_response,
        DurationSeconds=3600 * 12
    )
    pprint(response)
    credentials = response['Credentials']

    credentials_ini = (pathlib.Path.home() / '.aws' / 'credentials')
    cp = ConfigParser()
    cp.read(credentials_ini)

    account_name = accounts_by_number.get(account_number, account_number)

    for section in {'default', account_name}:
        cp.remove_section(section)
        cp.add_section(section)
        cp.set(section, 'aws_access_key_id', credentials['AccessKeyId'])
        cp.set(section, 'aws_secret_access_key', credentials['SecretAccessKey'])
        cp.set(section, 'aws_session_token', credentials['SessionToken'])

    with open(credentials_ini, mode='w') as fo:
        cp.write(fo)

    return credentials_ini
    
    
def stop():
    from threading import Thread
    def fn():
        httpd.shutdown()
        httpd.server_close()
        
    Thread(target=fn).start()


class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    principal_name: str

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length).decode('utf-8')
        print(request_body)
        request_dict = json.loads(request_body)
        pprint(request_dict)
        if self.path == '/saml':
            status = 200
            try:
                credentials_ini = assume_role_with_saml(
                    request_dict['SAMLResponse'], request_dict['roleARN'], self.principal_name
                )
                body = {'credentials_ini': str(credentials_ini)}
            except Exception as e:
                status = 400
                body = {'error': str(e)}

            self.send_response(status)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(body), encoding='utf8'))
            stop()
        else:
            self.send_error(404, self.path)


def run(identity_provider_name: str):
    global httpd
    server_address = ('127.0.0.1', 9123)
    print(f'Starting assume_role_with_saml at {server_address}.\nWaiting for web client extension requests ...')
    MyHttpRequestHandler.principal_name = identity_provider_name
    httpd = HTTPServer(server_address, MyHttpRequestHandler)
    httpd.serve_forever()
