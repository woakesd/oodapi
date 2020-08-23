import os
import azure.functions
import logging
import aiomysql
import scrypt
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from base64 import b64encode
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
        return False, { 'error': 'user or password not recognized' }
    return True, { 'sub': f'{id[:8]}-{id[8:12]}-{id[12:16]}-{id[16:20]}-{id[20:]}' }
 
async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        body = req.get_json()
        logging.info(f'Got body {body}')
        auth, ident = await login(body['name'], body['pass'])
        if not auth:
            return azure.functions.HttpResponse(dumps(ident, default=str), status_code=401)
        ident['name'] = body['name']    
        ident['iss'] = 'oodapi'
        ident['iat'] = get_int_from_datetime(datetime.now(timezone.utc))
        ident['exp'] = get_int_from_datetime(datetime.now(timezone.utc) + timedelta(hours=1))
        signing_key = jwk_from_pem(os.environ['privateRSAKey'].encode())
        instance = JWT()
        token = { 'token': instance.encode(ident, signing_key, alg='RS256') }

        return azure.functions.HttpResponse(dumps(token, default=str), status_code=200)
    except Exception as e:
        logging.error(f"return failed, {e}")
        return azure.functions.HttpResponse(json.dumps({'fatal': e}), status_code=500)

