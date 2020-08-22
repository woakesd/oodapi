import os
import azure.functions
import logging
import aiomysql
import scrypt
from urllib.parse import urlparse
from base64 import b64encode
from json import dumps

def mysql_connection_details(url):
    par = urlparse(url)
    return {
        'user': par.username, 
        'password': par.password,
        'host': par.hostname,
        'port': par.port,
        'db': par.path[1:]
    }
 
async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        body = req.get_json()
        logging.info(f'Got body {body}')
        name = body['name']
        password = body['pass']
        logging.info(name)
        conn_string = os.environ['dbconnection']
        args = mysql_connection_details(conn_string)
        async with aiomysql.connect(**args) as conn:
            async with conn.cursor() as cur:
                logging.info(f'Checking password for {name}')
                await cur.execute('select hex(id), salt, pass from user where name = %s', name) 
                r = await cur.fetchone()
                id = r[0]
                salt = r[1]
                passhash = r[2]
                status_code = 200
                if passhash != b64encode(scrypt.hash(password, salt, buflen=96)).decode('utf-8'):
                    ret = { 'error': 'user or password not recognized' }
                    return azure.functions.HttpResponse(dumps(ret, default=str), status_code=401)
                ret = { 'id': f'{id[:8]}-{id[8:12]}-{id[12:16]}-{id[16:20]}-{id[20:]}' }
            
        return azure.functions.HttpResponse(dumps(ret, default=str), status_code=status_code)
    except Exception as e:
        logging.error(f"return failed, {e}")
        return azure.functions.HttpResponse('Error occured', status_code=500)

