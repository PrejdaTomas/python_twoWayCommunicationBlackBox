from AA_dependencies import Path
from AA_dependencies import threading
from AA_dependencies import logging
from AA_dependencies import loggingConfig
from AA_dependencies import pidPrint


class ThreadLogFilter(logging.Filter):
	def __init__(self, thread_name: str, *args, **kwargs) -> None:
		super(ThreadLogFilter, self).__init__(*args, **kwargs)
		self.thread_name = thread_name

	def filter(self, record: logging.LogRecord) -> bool:
		return record.threadName == self.thread_name


def start_thread_logging(threadLoggerName: str) -> logging.Logger:
	"""
	Add a log handler to separate file for current thread
	"""
	log_file	= Path(f"{threadLoggerName}.log")
	log_handler	= logging.FileHandler(log_file)
	
	log_handler.setLevel(logging.DEBUG)

	formatter	= logging.Formatter("%(asctime)-15s | %(threadName)-15s | %(levelname)-5s | %(message)s")
	log_handler.setFormatter(formatter)

	thread_name	= threading.current_thread().name
	log_filter	= ThreadLogFilter(thread_name=  thread_name)
	log_handler.addFilter(log_filter)

	logger		= logging.getLogger()
	logger.addHandler(log_handler)

	return log_handler


def stop_thread_logging(log_handler) -> None:
	# Remove thread log handler from root logger
	logging.getLogger().removeHandler(log_handler)

	# Close the thread log handler so that the lock on log file can be released
	log_handler.close()


def out_ThreadLogger(funcIpt: bool):
	thread_log_handler = start_thread_logging()
	logging.info('Info log entry in sub thread.')
	logging.debug('Debug log entry in sub thread.')
	stop_thread_logging(thread_log_handler)


def config_root_logger(globalLoggerName: str):
	log_file = f"{globalLoggerName}.log"

	formatter = "%(asctime)-15s | %(threadName)-11s | %(levelname)-5s | %(message)s"

	loggingConfig.dictConfig({
		'version': 1,
		'formatters': {
			'root_formatter': {
				'format': formatter
			}
		},
		
		'handlers': {
			'console': {
				'level': 'INFO',
				'class': 'logging.StreamHandler',
				'formatter': 'root_formatter'
			},
			'log_file': {
				'class': 'logging.FileHandler',
				'level': 'DEBUG',
				'filename': log_file,
				'formatter': 'root_formatter',
			}
		},
		
		'loggers': {
			'': {
				'handlers': [
					'console',
					'log_file',
				],
				'level': 'DEBUG',
				'propagate': True
			}
		}
	})