Creates temporary AWS security credentials from a SAML authentication response.
You install less than 150 lines of code with no external dependencies except `boto3`, which you probably need anyway.

# How Does it Work

A Chrome Extension adds the button `Assume Role` to Amazon Web Services Sign-In:
![signin.png](signin.png)

Clicking the `Assume Role` button calls a small local web server, which writes temporary AWS credentials to the shared
credential file (~/.aws/credentials).

# Setup

1. Clone this project.
2. Optionally create virtual environment and install boto3.
3. Add this Chrome Extension according to [Getting started - Chrome Developers](https://developer.chrome.com/docs/extensions/mv2/getstarted/#manifest):
    1. Open the Extension Management page by navigating to chrome://extensions.
    2. Enable Developer Mode by clicking the toggle switch next to Developer mode.
    3. Click the LOAD UNPACKED button and select the project (=extension) directory.

# Configure

Provide a starter script of the form

````
import webbrowser
import server

# Optionally open sso page
webbrowser.open_new('https://my_single_sign_on_client')
server.run(principal_name='my_principal_name')
````

Constructs a PrincipalArn of the form 'arn:aws:iam::{my_account}:saml-provider/{my_principal_name}'

# Run

````
C:\ws\tools\PortableGit\git-bash.exe -c "cd c:/ws/projects/assume_role_with_saml; venv/scripts/python.exe my_assume_role.py"
````

# Security Considerations

Due to its local nature, no attack vectors are added.

However, a user may inadvertently click the `Assume Role` button. The user will then not realize that the
shared AWS credentials were changed. AWS SDK API calls may now run on an account the user does not expect.

# Related Work

* https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
* https://github.com/prolane/samltoawsstskeys
* https://chrome.google.com/webstore/detail/console-recorder-for-aws
* https://github.com/sportradar/aws-azure-login

