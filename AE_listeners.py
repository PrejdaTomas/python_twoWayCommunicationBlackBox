from AA_dependencies import typing
from AA_dependencies import Path
from AA_dependencies import os
from AA_dependencies import pidPrint
from AA_dependencies import constants
from AA_dependencies import sleep
from AA_dependencies import AB_signals
from AA_dependencies import AD_IO
from AA_dependencies import AC_decorators


@AC_decorators.verboser
def threadFunc_listenToFile(outFile: Path) -> None:
	AD_IO.waitTillFileExists_stupid(filePath=outFile)
	with open(outFile, "rb") as readPort:
		while not constants.stop_flag.is_set():
			if AD_IO.getFileSizeInBytesForAnConstantlyOpenedChangingFile(readPortInput=readPort) > 0:
				lines = AD_IO.readLastNLines(readPortInput=readPort, bufferSize=1024, numberOfLines=5)
				for index, line in enumerate(lines): pidPrint(f"threadFunc_listenToFile: line_{str(index).zfill(3)} = {line}")
			sleep(0.05)
	# else:
	# 	raise FileNotFoundError(f"[{os.getpid()}]: threadFunc_listenToFile: file not found: {outFile}")


@AC_decorators.verboser
def threadFunc_listenToSTDOUT(pipe: typing.IO) -> None:
	while not constants.stop_flag.is_set():
		line = pipe.readline()
		if line: pidPrint(f"threadFunc_listenToSTDOUT: {line=}")
		else: break
		sleep(0.1)

	# for _ in range(5):
	# 	try:
	# 		line = pipe.readline()
	# 		if line: pidPrint(f"{line=}")
	# 	except: pass
	pipe.close()

