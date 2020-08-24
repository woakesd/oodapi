import os
import azure.functions
import logging
import aiomysql
import scrypt
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from base64 import b64encode, b64decode
from json import dumps
from jwt import JWT, jwk_from_pem
from jwt.utils import get_int_from_datetime

def mysql_connection_details(url):
    par = urlparse(url)
    return {
        'user': par.username, 
        'password': par.password,
        'host': par.hostname,
        'port': par.port,
        'db': par.path[1:]
    }

def get_signing_key():
    private_key_data = os.environ['privateRSAKey']
    return jwk_from_pem(b64decode(os.environ['privateRSAKey']))


async def login(name: str, password: str) -> dict:
    logging.info(f'{name} is attempting to log in')
    conn_string = os.environ['dbconnection']
    args = mysql_connection_details(conn_string)
    async with aiomysql.connect(**args) as conn:
        async with conn.cursor() as cur:
            logging.info(f'Checking password for {name}')
            await cur.execute('select hex(id), salt, pass from user where name = %s', name) 
            id, salt, passhash = await cur.fetchone()
    if passhash != b64encode(scrypt.hash(password, salt, buflen=96)).decode('utf-8'):
        return False, None, 'user or password not recognized'
    return True, f'{id[:8]}-{id[8:12]}-{id[12:16]}-{id[16:20]}-{id[20:]}', None
 
def get_jwt(subject, name, issuer):
    ident = {
        'sub': subject,
        'name': name,
        'iss': issuer,
        'iat': get_int_from_datetime(datetime.now(timezone.utc)),
        'exp': get_int_from_datetime(datetime.now(timezone.utc) + timedelta(hours=1))
    }

    signing_key = get_signing_key()

    instance = JWT()

    return instance.encode(ident, signing_key, alg='RS256')

async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        body = req.get_json()
        logging.debug(f'Got body {body}')

        auth, subject, error = await login(body['name'], body['pass'])

        if not auth:
            return azure.functions.HttpResponse(dumps({'error': error}, default=str), status_code=401)

        token = get_jwt(subject, body['name'], 'oodapi')

        return azure.functions.HttpResponse(dumps({'token': token}, default=str), status_code=200)

    except Exception as e:
        logging.error(f"Failure, {e}")

        return azure.functions.HttpResponse(dumps({'fatal': e}, default=str), status_code=500)

