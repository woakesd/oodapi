import os
import azure.functions
import logging
import scrypt
from base64 import b64encode, b64decode
from json import dumps
from jwt import JWT, jwk_from_pem
from jwt.exceptions import JWTDecodeError

def get_signing_key():
    private_key_data = os.environ['privateRSAKey']
    return jwk_from_pem(b64decode(os.environ['privateRSAKey']))


def verify_jwt(token):

    signing_key = get_signing_key()

    instance = JWT()

    return instance.decode(token, signing_key)

async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        token = req.route_params.get('token')
        logging.debug(f'Got token {token}')

        try:
            message = verify_jwt(token)
        except JWTDecodeError as e:
            return azure.functions.HttpResponse(dumps({'error': e}, default=str), status_code=401)

        return azure.functions.HttpResponse(dumps(message, default=str), status_code=200)

    except Exception as e:
        logging.error(f"Failure, {e}")

        return azure.functions.HttpResponse(dumps({'fatal': e}, default=str), status_code=500)

