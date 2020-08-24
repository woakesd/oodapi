import os
from urllib.parse import urlparse
import aiomysql
import logging

def mysql_connection_details(url):
    par = urlparse(url)
    return {
        'user': par.username, 
        'password': par.password,
        'host': par.hostname,
        'port': par.port,
        'db': par.path[1:]
    }

async def get_rows_as_dict_array(sql, *args):
    conn_string = os.environ['dbconnection']
    logging.info(f'{sql}')
    logging.info(f'{args}')
    conn_args = mysql_connection_details(conn_string)
    async with aiomysql.connect(**conn_args) as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, args) 
            columns = [column[0] for column in cur.description]
            return [dict(zip(columns, r)) for r in await cur.fetchall()]
                

