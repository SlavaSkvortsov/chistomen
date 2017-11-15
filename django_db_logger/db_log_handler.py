# -*- coding: utf-8 -*-
import logging


class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from django_db_logger.models import StatusLog

        kwargs = {
            'logger_name': record.name,
            'level': record.levelno,
            'msg': record.getMessage(),
            'trace': getattr(record, 'trace', None),
            'user_id': getattr(record, 'user_id', None)
        }        
        StatusLog.objects.create(**kwargs)
