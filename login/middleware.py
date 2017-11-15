from garbage.middleware import LoggingMiddleware


class LoginLoggingMiddleware(LoggingMiddleware):
    """
    логирующая прослойка
    """
    request_startswith = '/login'
    logger_name = 'login'