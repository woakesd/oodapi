import os
import azure.functions
import logging
from json import dumps
from __app__.auth_lib import authorization

@authorization
async def main(req: azure.functions.HttpRequest, payload) -> azure.functions.HttpResponse:
    try:
        logging.debug(f'Got payload {payload}')

        return azure.functions.HttpResponse(dumps(payload, default=str), status_code=200)

    except Exception as e:
        logging.error(f"Failure, {e}")

        return azure.functions.HttpResponse(dumps({'fatal': e}, default=str), status_code=500)

