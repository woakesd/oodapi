import os
from urllib.parse import urlparse
import aiomysql
import logging

def mysql_connection_details():
    conn_string = os.environ['dbconnection']
    par = urlparse(conn_string)
    return {
        'user': par.username, 
        'password': par.password,
        'host': par.hostname,
        'port': par.port,
        'db': par.path[1:]
    }

async def get_rows_as_dict_array(sql, *args):
    logging.debug(f'{sql}')
    logging.debug(f'{args}')
    async with aiomysql.connect(**mysql_connection_details()) as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, args) 
            columns = [column[0] for column in cur.description]
            return [dict(zip(columns, r)) for r in await cur.fetchall()]
                
async def get_one_row(sql, *args):
    logging.debug(f'{sql}')
    logging.debug(f'{args}')
    async with aiomysql.connect(**mysql_connection_details()) as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, *args)
            return await cur.fetchone()
