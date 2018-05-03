import logging
from logging.config import dictConfig


class GNLogger:
    class Config:
        class GNFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord):
                return '{time} [{level}] [{pid}] {logger_name}:{lineno} {msg}'.format(
                    time=self.formatTime(record, self.datefmt),
                    level=record.levelname,
                    pid=record.process,
                    logger_name=record.name,
                    lineno=record.lineno,
                    msg=record.getMessage())

        DEV = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    '()': GNFormatter
                },
            },
            'handlers': {
                'default': {
                    'level': 'DEBUG',
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['default'],
                    'level': 'DEBUG',
                    'propagate': True
                },
            }
        }

    dictConfig(Config.DEV)

    @classmethod
    def get_logger(cls, logger_name: str) -> logging.Logger:
        return logging.getLogger(logger_name)
