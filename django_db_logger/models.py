# -*- coding: utf-8 -*-
import logging

from django.db import models

LOG_LEVELS = (
    (logging.NOTSET, 'NotSet'),
    (logging.INFO, 'Info'),
    (logging.WARNING, 'Warning'),
    (logging.DEBUG, 'Debug'),
    (logging.ERROR, 'Error'),
    (logging.FATAL, 'Fatal'),
)


class StatusLog(models.Model):
    logger_name = models.CharField(max_length=100, db_index=True)
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS, default=logging.ERROR)
    msg = models.TextField()
    trace = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True)
    user_id = models.BigIntegerField(null=True, db_index=True)

    def __str__(self):
        return 'StatusLog record #{0}'.format(self.pk)

    class Meta:
        ordering = ('-id',)
        index_together = [('create_datetime', 'level')]
