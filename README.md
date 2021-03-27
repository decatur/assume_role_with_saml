````
python assume_role_with_saml/server.py --PrincipalName my_saml_provider_name
C:\ws\tools\PortableGit\git-bash.exe -c "c:/ws/projects/playground/venv/scripts/python assume_role_with_saml/server.py"
````

Constructs a PrincipalArn of the form 'arn:aws:iam::{account}:saml-provider/{PrincipalName}'

![signin.png](signin.png)

Less than 150 lines of code, no external dependencies but `boto3`, which you probably need anyway

# Related Work
* https://github.com/prolane/samltoawsstskeys
* https://chrome.google.com/webstore/detail/console-recorder-for-aws
* https://github.com/sportradar/aws-azure-login
