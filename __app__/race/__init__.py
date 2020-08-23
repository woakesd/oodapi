import os
import azure.functions
import logging
from urllib.parse import urlparse
import aiomysql
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
        rid = req.route_params.get('rid')
        logging.info(rid)
        conn_string = os.environ['dbconnection']
        args = mysql_connection_details(conn_string)
        async with aiomysql.connect(**args) as conn:
            async with conn.cursor() as cur:
                await cur.execute('select * from races_new where rid = %s', rid) 
                columns = [column[0] for column in cur.description]
                r = [dict(zip(columns, r)) for r in await cur.fetchall()]
        return azure.functions.HttpResponse(dumps(r, default=str))
    except Exception as e:
        logging.error(f"return failed, {e}")
        return azure.functions.HttpResponse({'error': e}, status_code=500)
