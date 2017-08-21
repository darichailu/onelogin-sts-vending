from flask import Flask, render_template, json, request
import boto3
import urllib3
import json
import os 
app = Flask(__name__)




@app.route("/")
def main():
    return render_template('index.html')


@app.route('/login',methods=['POST'])
def login():
 
    # read the posted values from the UI
    _email = request.form['username']
    _password = request.form['password']
 
    http = urllib3.PoolManager()

    tokenResponse = http.request(
        'POST',
        'https://api.us.onelogin.com/auth/oauth2/token',
        headers={
          'Authorization': 'client_id:{0}, client_secret:{1}'.format(os.environ['ONELOGIN_CLIENT_ID'], os.environ['ONELOGIN_CLIENT_SECRET']),
          'Content-Type': 'application/json'
        },
        body=json.dumps({'grant_type':'client_credentials'}).encode('utf-8')
        )

    assertionResponse = http.request(
        'POST',
        'https://api.us.onelogin.com/api/1/saml_assertion',
        headers={
          'Authorization': 'bearer:{0}'.format(json.loads(tokenResponse.data.decode('utf-8'))['data'][0]['access_token']),
          'Content-Type': 'application/json'
        },
        body=json.dumps({'username_or_email': _email, 'password': _password,'app_id': '678241', 'subdomain': 'innroad'}).encode('utf-8')
        )

    assertion=json.loads(assertionResponse.data.decode('utf-8'))['data']


    client = boto3.client('sts')
    credentialsResponse = client.assume_role_with_saml(
        RoleArn=os.environ['AWS_TARGET_ROLE_ARN'],
        PrincipalArn=os.environ['AWS_PRINCIPAL_ROLE_ARN'],
        SAMLAssertion=assertion,
        DurationSeconds=3600
    )

    #response.headers['Content-Type'] = 'application/json'
    response = {"AccessKey": credentialsResponse['Credentials']['AccessKeyId'], "SecretKey": credentialsResponse['Credentials']['SecretAccessKey'], "SessionToken": credentialsResponse['Credentials']['SessionToken']}

    return json.dumps(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
