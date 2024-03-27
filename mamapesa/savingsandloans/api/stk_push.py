import requests

def make_stk_push_request(amount, msisdn, account_reference):
    # Define the endpoint URL
    url = "https://payments.mamapesa.com/api/stkPush"

    # Define the payload data
    payload = {
        "amount": amount,
        "msisdn": msisdn,
        "account_reference": account_reference
    }

    try:
        # Make a POST request to the API endpoint with the payload data
        response = requests.post(url, json=payload)

        # Get the response code
        response_code = response.status_code

        # Check if the request was successful
        if response_code == 200:
            # Return the response code and data if successful
            return response_code, response.json()
        else:
            # Return the response code and error message if the request was unsuccessful
            return response_code, {"error": response.text}

    except requests.exceptions.RequestException as e:
        # Return a response code of -1 and the error message if there was an error making the request
        return -1, {"error": str(e)}
