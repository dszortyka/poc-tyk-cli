
import json
import os
from flask import Flask, Response, request
import requests
from jsonpath_ng import parse

app     = Flask(__name__)

def _patch_payload(payload, replace_opts=True, **kwargs) -> object:

    # Remove any duplicated argument if available in kwargs[opts]
    if replace_opts is True and kwargs['opts'] is not None:
        for x, y in kwargs.items():
            if x in kwargs['opts']:
                del(kwargs['opts'][x])

    # loop over kwargs fields, check if any is available in payload
    # if field is found, replace it with kwargs values
    for kwargs_key, kwargs_value in kwargs.items():
        if kwargs_key == "opts" and kwargs_value is not None:
            for item, value in kwargs_value.items():
                if item == "expires":   # for example purpose
                    value = int(value)
                # item = "$." + item
                jsonpath_expression = parse(item)
                for match in jsonpath_expression.find(payload):
                    jsonpath_expression.update(payload, value)
            continue

        # kwargs_key = "$." + kwargs_key
        jsonpath_expression = parse(kwargs_key)
        for match in jsonpath_expression.find(payload):
            jsonpath_expression.update(payload, kwargs_value)

    return payload


@app.route('/token/<l_type>', methods=['GET'])
def token(l_type):
    ''' 
    '''

    if l_type == "renew":
        
        tyk_api_key = os.getenv('TYK_API_KEY', None)
        tyk_gateway_env = os.getenv('TYK_GATEWAY_ENV', None)

        header = {}
        header['x-tyk-authorization'] = tyk_api_key

        try:
            key_id = request.headers['x_tykc_key']      # x-tykc-key -> is automatically changed to use underscore
        except:
            ret_message = f'x-tykc-key header must be provided!'
            return Response(ret_message, mimetype='application/json', status=404)

        header['Content-type'] = 'application/json'

        header['x-tykc-key'] = key_id


        url = f"{tyk_gateway_env}/tyk/keys/{key_id}"
        print(f"URL: {url}")
        response = requests.get(url, headers=header, verify=False)
        print(f"Response: {response}")

        key_payload = response.json()

        print(f"Key Retrieved from Tyk GW:\n{key_payload}")

        # patch the payload with the the new `expires` value

        current_expires = key_payload['expires']
        new_expires = int(current_expires) + 1
        kwargs = {}
        kwargs['expires'] = new_expires

        print(f"Current value for Expires: {current_expires}")
        print(f"New value for expires: {new_expires}")

        # patch the payload with the new value
        new_payload = _patch_payload(payload=key_payload, replace_opts=False, **kwargs)

        print(f"New Payload\n{new_payload}")

        # update the payload
        url = f"{tyk_gateway_env}/tyk/keys/{key_id}"
        response = requests.put(url, headers=header, data=json.dumps(new_payload, indent=2), verify=False)

        print(f"Response from Update command:\n{response.text}")

        return Response(json.dumps(new_payload), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
