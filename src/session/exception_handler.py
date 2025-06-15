import logging
import os
import jwt

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    request = context.get('request')
    if request:
        logger.debug(f"DEBUG: auth_header: {request.headers.get('Authorization')}")
    else:
        logger.debug("DEBUG: Request object not available in context.")

    jwt_signing_key_debug_value = os.environ.get('JWT_SIGNING_KEY', 'JWT_SIGNING_KEY_NOT_SET')
    logger.debug(f"DEBUG: JWT_SIGNING_KEY in handler: '{jwt_signing_key_debug_value}'")

    response = exception_handler(exc, context)

    request_path = request.path if request else "N/A"
    token_preview = "N/A"
    auth_header_present = False

    if request and request.headers.get('Authorization'):
        auth_header_present = True
        auth_header = request.headers.get('Authorization')
        if auth_header.startswith('Bearer '):
            token_part = auth_header.split(' ')[1]
            token_preview = token_part[:15] + '...' + token_part[-15:]

    if isinstance(exc, (TokenError, InvalidToken)):
        log_message = "JWT validation failed for request."
        log_extra = {
            'correlation_id': getattr(request, 'correlation_id', 'N/A'),
            'path': request_path,
            'error_type': type(exc).__name__,
            'error_message': str(exc.detail),
            'token_preview': token_preview,
        }
        try:
            if token_preview != "N/A":
                decoded_payload = jwt.decode(token_part, options={"verify_signature": False})
                log_extra['token_user_id_claim'] = decoded_payload.get('sub', 'N/A')
                log_extra['decoded_payload_debug'] = decoded_payload
            else:
                log_extra['token_user_id_claim'] = 'N/A (No token or malformed header)'
        except Exception as decode_error:
            log_extra['decode_error_message'] = str(decode_error)

        logger.warning(log_message, extra=log_extra)

        custom_response_data = {
            'errorCode': 'JWT_AUTH_FAILED',
            'message': str(exc.detail) if hasattr(exc, 'detail') else 'Erro de autenticação de token JWT.'
        }
        return Response(custom_response_data, status=status.HTTP_401_UNAUTHORIZED)

    elif isinstance(exc, AuthenticationFailed):
        log_message = "Authentication credentials not provided or invalid (DRF AuthenticationFailed)."
        log_extra = {
            'correlation_id': getattr(request, 'correlation_id', 'N/A'),
            'path': request_path,
            'error_type': type(exc).__name__,
            'error_message': str(exc.detail),
            'auth_header_present': auth_header_present,
            'token_preview': token_preview,
        }
        logger.warning(log_message, extra=log_extra)

        custom_response_data = {
            'errorCode': 'AUTH_REQUIRED',
            'message': str(exc.detail) if hasattr(exc, 'detail') else 'Credenciais de autenticação são necessárias.'
        }
        return Response(custom_response_data, status=status.HTTP_401_UNAUTHORIZED)
    return response
