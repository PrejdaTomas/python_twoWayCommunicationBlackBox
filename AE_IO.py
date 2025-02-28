from AA_dependencies import typing, os, Path
from AA_dependencies import sleep
#from AA_dependencies import watchdogEvents
#from AA_dependencies import watchdogObservers
from AA_dependencies import constants
from AA_dependencies import AD_decorators

def moveCursorToTheEnd(readPortInput: typing.IO) -> None:
	readPortInput.seek(	0,				#offset = pocet bajtu pro posun kurzoru (stride)
						os.SEEK_END		#whence = referencni misto pro kurzor
	)
	#SEEK_SET = 0
	#SEEK_CUR = 1
	#SEEK_END = 2


def getFileSizeInBytesForAnConstantlyOpenedChangingFile(readPortInput: typing.IO) -> int:
	moveCursorToTheEnd(readPortInput=readPortInput)
	byteSize = readPortInput.tell()
	return byteSize

def moveCursorSpecifiedBytesFromEnd(readPortInput: typing.IO, numberOfBytes: typing.Optional[int] = 1024) -> None:
	fileSize = getFileSizeInBytesForAnConstantlyOpenedChangingFile(readPortInput=readPortInput)
	readPortInput.seek(max(fileSize - numberOfBytes, 0), os.SEEK_SET)

def readLastNLines(readPortInput:  typing.IO, numberOfLines: typing.Optional[int] = 5, bufferSize: typing.Optional[int] = 1024) -> typing.List[str]:
	moveCursorSpecifiedBytesFromEnd(readPortInput= readPortInput, numberOfBytes=bufferSize)
	content: typing.List[str] = readPortInput.readlines()[numberOfLines:]
	return content

def readLastNBytes(readPortInput:  typing.IO, bufferSize: typing.Optional[int] = 1024) -> typing.List[str]:
	moveCursorSpecifiedBytesFromEnd(readPortInput= readPortInput, numberOfBytes=bufferSize)
	content: str = readPortInput.read()
	return content


# class FileCreatedHandler(watchdogEvents.FileSystemEventHandler):
# 	def __init__(self, filePath: Path) -> None:
# 		self.file_path = filePath
# 		self.file_created = False

# 	def on_created(self, event):
# 		print(self.file_path, event.src_path)
# 		if event.src_path == self.file_path:
# 			self.file_created = True

# @AD_decorators.checkTypesAtCorrespondingIndices(inputTypes=(Path,), argumentPositions=(0,))
# def waitTillFileExists(filePath: Path) -> None:
# 	event_handler = FileCreatedHandler(filePath)
# 	observer = watchdogObservers.Observer()
# 	fileDir = Path(os.path.dirname(filePath))
# 	observer.schedule(event_handler, path=fileDir, recursive=False)
# 	observer.start()

# 	try:
# 		while not (event_handler.file_created or constants.stop_flag.is_set()):
# 			sleep(0.1)
# 	finally:
# 		observer.stop()
# 		observer.join()

@AD_decorators.checkTypesAtCorrespondingIndices(inputTypes=(Path,), argumentPositions=(0,))
def waitTillFileExists_stupid(filePath: Path) -> None:
	while not os.path.exists(filePath):
		sleep(0.1)