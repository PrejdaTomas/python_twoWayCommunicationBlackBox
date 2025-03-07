import logging.handlers
from AA_dependencies import os
from AA_dependencies import typing
from AA_dependencies import itertools
from AA_dependencies import datetime
from AA_dependencies import Path
from AA_dependencies import threading
from AA_dependencies import logging
from AA_dependencies import loggingConfig
from AA_dependencies import loggingHandlers
from AA_dependencies import pidPrint


class ThreadLogFilter(logging.Filter):
	def __init__(self, thread_name: str, *args, **kwargs) -> None:
		super(ThreadLogFilter, self).__init__(*args, **kwargs)
		self.thread_name = thread_name

	def filter(self, record: logging.LogRecord) -> bool:
		return record.threadName == self.thread_name

def getRootLoggerFileHandler() -> logging.FileHandler:
	rootLogger		= logging.getLogger()
	for handler in rootLogger.handlers:
		if isinstance (handler, logging.FileHandler):
			break
	return handler

def start_thread_logging(threadLoggerName: str) -> logging.Logger:
	"""
	Add a log handler to separate file for current thread
	"""
	rootLogger		= logging.getLogger()
	rootLoggerFileHandler = getRootLoggerFileHandler()
	logsDir = Path(os.path.dirname(rootLoggerFileHandler.baseFilename))

	log_file	= Path(os.path.join(logsDir, f"{threadLoggerName}.log"))
	log_handler	= logging.FileHandler(log_file)
	
	log_handler.setLevel(logging.DEBUG)

	formatter	= logging.Formatter("%(asctime)-15s | %(threadName)-15s | %(levelname)-5s | %(message)s")
	log_handler.setFormatter(formatter)

	thread_name	= threading.current_thread().name
	log_filter	= ThreadLogFilter(thread_name=  thread_name)
	log_handler.addFilter(log_filter)

	rootLogger		= logging.getLogger()
	rootLogger.addHandler(log_handler)

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
	logsDir = Path("logs")
	if not os.path.exists(logsDir): os.mkdir(logsDir)
 
	log_file = Path(os.path.join(logsDir, f"{globalLoggerName}_main.log"))

	formatter = "%(asctime)-15s | %(threadName)-11s | %(levelname)-5s | %(message)s"

	_configDict = {
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
	}

	# _configDict = {
	# 		'version': 1,
	# 		'formatters': {
	# 			'root_formatter': {
	# 				'format': formatter
	# 			}
	# 		},
	# 		'handlers': {
	# 			'log_file': {
	# 				'class': 'logging.FileHandler',
	# 				'level': 'DEBUG',
	# 				'filename': log_file,
	# 				'formatter': 'root_formatter',
	# 			}
	# 		},
	# 		'root': {
	# 			'handlers': ['log_file'],
	# 			'level': 'DEBUG',
	# 		}
	# 	}
	loggingConfig.dictConfig(_configDict)


def combineLogs() -> None:
	logsDir = Path("logs")
	logFiles = [os.path.join(logsDir, file) for file in os.listdir(logsDir) if "_main.log" in file]

	def generator(filePath: Path) -> typing.Generator[typing.Tuple[Path,str], None, None]:
		with open(filePath, "r") as readPort:
			while True:
				try:
					yield (os.path.split(os.path.splitext(filePath)[0])[-1]).ljust(20, ' '), next(readPort).strip()
				except StopIteration:
					break

	def lineProcessor(lineInput: str) -> typing.Tuple[float, str]:
		textStart = lineInput.find('|')
		timeStamp = datetime.fromisoformat(lineInput[:textStart].strip()).timestamp()
		content = lineInput[textStart:].strip()
		return timeStamp, content

	with open("002_combined.log", "w") as writePort:
		textGens = itertools.cycle([generator(filePath) for filePath in logFiles])
		filePrev: str = (os.path.split(os.path.splitext(logFiles[0])[0])[-1]).ljust(20, ' ')
		timeStampPrev: float = 0.0
		lineContentPrev: str = ""

		fileNext: str = ""
		timeStampNext: float = 1.0
		lineContentNext: str = ""

		while True:
			filePrev, timeStampPrev, lineContentPrev = fileNext, timeStampNext, lineContentNext

			try:
				generatorUsed = next(textGens)
				fileNext, line = next(generatorUsed)
				timeStampNext, lineContentNext = lineProcessor(line)
			except StopIteration:
				break

			writePort.write(f"{datetime.fromtimestamp(timeStampNext)} | {fileNext} {lineContentNext}\n")
			#if iteration == 20: break
   

import heapq
def combineLogs() -> None:
	logsDir = Path("logs")
	logFiles = [os.path.join(logsDir, file) for file in os.listdir(logsDir) if "_main.log" in file]

	def generator(filePath: Path) -> typing.Generator[str, None, None]:
		with open(filePath, "r") as readPort:
			for line in readPort:
				yield line.strip()

	def lineProcessor(lineInput: str) -> typing.Tuple[float, str]:
		textStart = lineInput.find('|')
		timeStamp = datetime.fromisoformat(lineInput[:textStart].strip()).timestamp()
		content = lineInput[textStart:].strip()
		return timeStamp, content

	with open("002_combined.log", "w") as writePort:
		textGens = [generator(filePath) for filePath in logFiles]
		heap = []

		# Initialize the heap with the first line from each generator
		for gen in textGens:
			try:
				line = next(gen)
				heapq.heappush(heap, (lineProcessor(line), gen))
			except StopIteration:
				pass

		while heap:
			(timeStamp, lineContent), gen = heapq.heappop(heap)
			writePort.write(f"{datetime.fromtimestamp(timeStamp)} | {lineContent}\n")

			try:
				next_line = next(gen)
				heapq.heappush(heap, (lineProcessor(next_line), gen))
			except StopIteration:
				pass

def combineLogs() -> None:
	logsDir = Path("logs")
	logFiles = [os.path.join(logsDir, file) for file in os.listdir(logsDir) if "_main.log" in file]

	def generator(filePath: Path) -> typing.Generator[str, None, None]:
		with open(filePath, "r") as readPort:
			for line in readPort:
				yield line.strip()

	def lineProcessor(lineInput: str) -> typing.Tuple[float, str]:
		textStart = lineInput.find('|')
		timeStamp = datetime.fromisoformat(lineInput[:textStart].strip()).timestamp()
		content = lineInput[textStart:].strip()
		return timeStamp, content

	with open("002_combined.log", "w") as writePort:
		textGens = [generator(filePath) for filePath in logFiles]
		heap = []

		# Initialize the heap with the first line from each generator
		for gen in textGens:
			try:
				line = next(gen)
				timeStamp, content = lineProcessor(line)
				heapq.heappush(heap, (timeStamp, content, gen))
			except StopIteration:
				pass

		while heap:
			timeStamp, lineContent, gen = heapq.heappop(heap)
			writePort.write(f"{datetime.fromtimestamp(timeStamp)} | {lineContent}\n")

			try:
				next_line = next(gen)
				next_timeStamp, next_content = lineProcessor(next_line)
				heapq.heappush(heap, (next_timeStamp, next_content, gen))
			except StopIteration:
				pass

def combineLogs() -> None:
	logsDir = Path("logs")
	logFiles = [os.path.join(logsDir, file) for file in os.listdir(logsDir) if "_main.log" in file]

	def generator(filePath: Path) -> typing.Generator[str, None, None]:
		with open(filePath, "r") as readPort:
			for line in readPort:
				yield line.strip()

	def lineProcessor(lineInput: str) -> typing.Tuple[float, str]:
		textStart = lineInput.find('|')
		timeStamp = datetime.fromisoformat(lineInput[:textStart].strip()).timestamp()
		content = lineInput[textStart:].strip()
		return timeStamp, content

	with open("002_combined.log", "w") as writePort:
		textGens = [generator(filePath) for filePath in logFiles]
		heap = []

		# Initialize the heap with the first line from each generator
		for gen in textGens:
			try:
				line = next(gen)
				timeStamp, content = lineProcessor(line)
				heapq.heappush(heap, (timeStamp, content, gen))
			except StopIteration:
				pass

		while heap:
			timeStamp, lineContent, gen = heapq.heappop(heap)
			writePort.write(f"{datetime.fromtimestamp(timeStamp)} | {lineContent}\n")

			try:
				next_line = next(gen)
				next_timeStamp, next_content = lineProcessor(next_line)
				heapq.heappush(heap, (next_timeStamp, next_content, gen))
			except StopIteration:
				pass

class LogEntry:
	def __init__(self, timestamp: float, content: str, generator: typing.Generator[str, None, None], logFile: Path):
		self.timestamp = timestamp
		self.content = content
		self.generator = generator
		self.logFile = (os.path.split(os.path.splitext(logFile)[0])[-1]).ljust(16, ' ')

	def __lt__(self, other):
		return self.timestamp < other.timestamp


def combineLogs() -> None:
	logsDir = Path("logs")
	logFiles = [os.path.join(logsDir, file) for file in os.listdir(logsDir) if "_main.log" in file]
	totalLogger = Path(os.path.join(logsDir, "002_combined.log"))
	def generator(filePath: Path) -> typing.Generator[typing.Tuple[Path, str], None, None]:
		with open(filePath, "r") as readPort:
			for line in readPort:
				yield filePath, line.strip()

	def lineProcessor(lineInput: str) -> typing.Tuple[float, str]:
		textStart = lineInput.find('|')
		timeStamp = datetime.fromisoformat(lineInput[:textStart].strip()).timestamp()
		content = lineInput[textStart:].strip()
		return timeStamp, content

	with open(totalLogger, "w") as writePort:
		textGens = [generator(filePath) for filePath in logFiles]
		heap = []

		# Initialize the heap with the first line from each generator
		for gen in textGens:
			try:
				path, line = next(gen)
				timeStamp, content = lineProcessor(line)
				heapq.heappush(heap, LogEntry(timeStamp, content, gen, path))
			except StopIteration: pass

		while heap:
			logEntry = heapq.heappop(heap)
			writePort.write(f"{datetime.fromtimestamp(logEntry.timestamp)}| {logEntry.logFile}| {logEntry.content}\n")

			try:
				path, next_line = next(logEntry.generator)
				next_timeStamp, next_content = lineProcessor(next_line)
				heapq.heappush(heap, LogEntry(next_timeStamp, next_content, logEntry.generator, logEntry.logFile))
			except StopIteration: pass