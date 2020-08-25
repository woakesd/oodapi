import os
import azure.functions
import logging
import scrypt
from base64 import b64encode, b64decode
from json import dumps
from jwt import JWT, jwk_from_pem
from jwt.exceptions import JWTDecodeError
from __app__.auth_lib import authorization

@authorization
async def main(req: azure.functions.HttpRequest, payload) -> azure.functions.HttpResponse:
    try:
        logging.debug(f'Got payload {payload}')

        return azure.functions.HttpResponse(dumps(payload, default=str), status_code=200)

    except Exception as e:
        logging.error(f"Failure, {e}")

        return azure.functions.HttpResponse(dumps({'fatal': e}, default=str), status_code=500)

