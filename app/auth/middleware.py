import logging
from functools import wraps
from flask import request, jsonify, abort
from app.services.auth_service import validate_scope, authenticate_with_bearer
from config import Config

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if Config.ENVIRONMENT == 'development':
            return f(*args, **kwargs)

        auth_header = request.headers.get('Authorization')
        scope_header = request.headers.get('X-Authorization-Scopes')

        logging.info(f"Auth header: {auth_header}")
        logging.info(f"Scope header: {scope_header}")

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if authenticate_with_bearer(token):
                logging.info("Bearer token authentication successful")
                return f(*args, **kwargs)
            logging.info("Bearer token authentication failed")
        
        if scope_header:
            if validate_scope(scope_header):
                logging.info("Scope validation successful")
                return f(*args, **kwargs)
            else:
                logging.info("Invalid or insufficient scope")
                abort(403, "Invalid or insufficient scope")
        else:
            logging.info("Authentication required")
            abort(401, "Authentication required")

    return decorated
