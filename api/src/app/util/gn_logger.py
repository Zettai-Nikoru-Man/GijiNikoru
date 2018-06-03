import logging
from logging.config import dictConfig

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class GNLogger:
    class Config:
        class GNFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord):
                return '{time} [{level}] [{pid}] {logger_name}:{lineno} {msg}'.format(
                    time=self.formatTime(record, self.datefmt),
                    level=record.levelname,
                    pid=record.process,
                    logger_name=record.pathname,
                    lineno=record.lineno,
                    msg=record.getMessage())

        DEV = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'standard': {
                    '()': GNFormatter
                },
            },
            'handlers': {
                'default': {
                    'level': 'INFO',
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                },
                'file': {
                    'level': 'INFO',
                    'formatter': 'standard',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': '/tmp/giji_nikoru/gn.log',
                    'mode': 'a',
                    'maxBytes': 10485760,
                    'backupCount': 5,
                },
            },
            'loggers': {
                '': {
                    'handlers': ['default', 'file'],
                    'level': 'INFO',
                    'propagate': True
                },
            }
        }

    dictConfig(Config.DEV)

    @classmethod
    def get_logger(cls, logger_name: str) -> logging.Logger:
        return logging.getLogger(logger_name)
