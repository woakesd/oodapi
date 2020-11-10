import os
import azure.functions
import logging
from json import dumps

from __app__.shared.auth_lib import login, LoginResult, get_jwt

async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        body = req.get_json()
        logging.debug(f'Got body {body}')

        login_result: LoginResult = await login(body['name'], body['pass'])

        if not login_result.status:
            return azure.functions.HttpResponse(dumps({'error': login_status.error_message}, default=str), status_code=401)

        token = get_jwt(login_result.subject, body['name'], 'oodapi')

        return azure.functions.HttpResponse(dumps({'token': token}, default=str), status_code=200)

    except Exception as e:
        logging.error(f"Failure, {e}")

        return azure.functions.HttpResponse(dumps({'fatal': e}, default=str), status_code=500)

