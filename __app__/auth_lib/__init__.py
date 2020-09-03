"""
Code used to login users and verify jwt tokens
"""
import os
import scrypt
import azure.functions
import logging
from json import dumps
from datetime import datetime, timedelta, timezone
from base64 import b64encode, b64decode
from jwt import JWT, jwk_from_pem
from jwt.utils import get_int_from_datetime
from jwt.exceptions import JWTDecodeError
from uuid import uuid4, UUID

from __app__.shared.database import get_one_row, execute_many, execute_multiple

async def login(name: str, password: str) -> dict:
    logging.info(f'{name} is attempting to log in')

    logging.info(f'Checking password for {name}')
    id, salt, passhash = await get_one_row('select id, salt, pass from user where name = %s', name) 
    if passhash != b64encode(scrypt.hash(password, salt, buflen=96)).decode('utf-8'):
        return False, None, 'user or password not recognized'

    subject = uuid4()
    await execute_many(
        'INSERT INTO user_session (id, user_id, expires) VALUES (%s, %s, %s)',
        [(subject.bytes, id, datetime.now(timezone.utc) + timedelta(hours=1))])
    
    return True, f'{subject}', None
 
def get_signing_key():
    private_key_data = os.environ['privateRSAKey']
    return jwk_from_pem(b64decode(os.environ['privateRSAKey']))

def get_jwt(subject, name, issuer):
    ident = {
        'sub': subject,
        'name': name,
        'iss': issuer,
        'iat': get_int_from_datetime(datetime.now(timezone.utc)),
    }

    signing_key = get_signing_key()

    instance = JWT()

    return instance.encode(ident, signing_key, alg='RS256')

def verify_jwt(token):

    signing_key = get_signing_key()

    instance = JWT()

    return instance.decode(token, signing_key)

def authorization(func):
    """
    This checks authentication!
    """
    async def check_token(req):
        auth_header = req.headers.get('Authorization', '')
        logging.debug(auth_header)
        if not auth_header.startswith('Bearer '):
            return error_return("Not authorized", 401)
        try:
            payload = verify_jwt(auth_header[7:])
            logging.debug(payload)
        except JWTDecodeError as e:
            return error_return("Not authorized", 401)

        subject = UUID(payload['sub'])
        now = (datetime.now(timezone.utc))
        rowcount = await execute_multiple([
            { 'sql': 'DELETE FROM user_session WHERE expires < %s', 'rows': [now] },
            { 'sql': 'UPDATE user_session SET expires = %s WHERE id = %s', 'rows': [( now + timedelta(hours=1), subject.bytes )] }
        ])

        if rowcount[1] == 0:
            return error_return("Not authorized", 401)

        return await func(req, payload)

    return check_token

def error_return(msg, status_code):
    return azure.functions.HttpResponse(dumps({'error': msg}, default=str), status_code=status_code)
