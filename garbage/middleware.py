import logging
import time

from rest_framework import status


class LoggingMiddleware(object):
    """
    логирующая прослойка
    """
    request_startswith = ''
    logger_name = __name__

    def __init__(self, get_response):
        self.get_response = get_response
        self._log = logging.getLogger(self.logger_name)

    def __call__(self, request):
        request_body = ""
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.path.startswith(self.request_startswith):
            request.logger = self._log
            start_time = time.time()
            if request.body:
                request_body = "".join(["\n\n", request.body.decode("utf-8")])

            self._log.debug("Запрос #%s %s %s %s %s",
                            id(request), request.method, request.path, request.GET.dict(), request_body)

        try:
            response = self.get_response(request)
        except Exception as ex:
            self._log.error(ex)
            raise

        # Code to be executed for each request/response after
        # the view is called.

        if request.path.startswith(self.request_startswith):
            if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_202_ACCEPTED]:
                log_method = self._log.info
            else:
                log_method = self._log.error

            log_method("Ответ на запрос #%s (%s %s %s %s) \n---%s c---\n%s %s\n%s\n\n%s",
                       id(request),
                       request.method, request.path, request.GET.dict(), request_body,
                       round(time.time() - start_time, 3),
                       response.status_code, response.reason_phrase,
                       "\n".join(["{0}:{1}".format(k, v) for k, v in response.items()]),
                       response.content.decode("utf-8"))

        return response


class GarbageLoggingMiddleware(LoggingMiddleware):
    request_startswith = '/garbage'
    logger_name = 'garbage'
