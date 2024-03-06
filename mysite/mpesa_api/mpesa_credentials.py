import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64


class MpesaC2bCredential:
    """
    This class is used to store the Mpesa C2B credentials required to access the API.
    """
    consumer_key = 'cHnkwYIgBbrxlgBoneczmIJFXVm0oHky'
    consumer_secret = '2nHEyWSD4VjpNh2g'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'


class MpesaAccessToken:
    """
   This class is used to retrieve the access token from Mpesa API.
   """
    r = requests.get(MpesaC2bCredential.api_URL,
                     auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
    # print(r.text)
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']


class LipanaMpesaPpassword:
    """
   This class is used to generate the Lipa Na Mpesa Online Password.
   """
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "4084887"
    Test_c2b_shortcode = "600344"
    passkey = 'a5ce9f8f9b6621de9573b4f3eac5d2f3c245e4fefe96722be3ce2c421277f960'

    data_to_encode = Business_short_code + passkey + lipa_time

    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')

