from AA_dependencies import typing
from AA_dependencies import Path
from AA_dependencies import os
from AA_dependencies import pidPrint
from AA_dependencies import constants
from AA_dependencies import sleep
from AA_dependencies import AB_logging
from AA_dependencies import AC_signals
from AA_dependencies import AE_IO
from AA_dependencies import AD_decorators


@AD_decorators.threadLogger
@AD_decorators.verboser
def listenToFile(outFile: Path) -> None:
	AE_IO.waitTillFileExists_stupid(filePath=outFile)
	with open(outFile, "rb") as readPort:
		while not constants.stop_flag.is_set():
			if AE_IO.getFileSizeInBytesForAnConstantlyOpenedChangingFile(readPortInput=readPort) > 0:
				lines = AE_IO.readLastNLines(readPortInput=readPort, bufferSize=1024, numberOfLines=5)
				for index, line in enumerate(lines): AB_logging.logging.info(f"listenToFile: line_{str(index).zfill(3)} = {line}")
			sleep(0.05)
	# else:
	# 	raise FileNotFoundError(f"[{os.getpid()}]: listenToFile: file not found: {outFile}")


@AD_decorators.threadLogger
@AD_decorators.verboser
def listenToPIPE(pipe: typing.IO) -> None:
	while not constants.stop_flag.is_set():
		line = pipe.readline()
		if line: AB_logging.logging.info(f"listenToPIPE: {line=}")
		else: break
		sleep(0.1)

	# for _ in range(5):
	# 	try:
	# 		line = pipe.readline()
	# 		if line: AB_logging.logging.info(f"{line=}")
	# 	except: pass
	pipe.close()

