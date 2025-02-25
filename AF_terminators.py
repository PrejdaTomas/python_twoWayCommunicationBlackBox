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
def threadFunc_terminateFromFile(outFile: Path, terminatoryWords: typing.Tuple[str,...]) -> None:
	sleep(0.1)
	AD_IO.waitTillFileExists_stupid(filePath=outFile)
	with open(outFile, "rb") as readPort:
		while not constants.stop_flag.is_set():
			if AD_IO.getFileSizeInBytesForAnConstantlyOpenedChangingFile(readPortInput=readPort) > 0:
				lines = AD_IO.readLastNLines(readPortInput=readPort, bufferSize=1024, numberOfLines=5)
				for line in lines:
					if any((killPhrase.encode() in line.strip() for killPhrase in terminatoryWords)):
						pidPrint(f"threadFunc_terminateFromSTDOUT for {outFile}: killPhrase detected: {line}! Terminating the program in 0.25 s!!!")
						sleep(0.25)
						constants.stop_flag.set()
						break
			else: break
			sleep(0.1)



@AC_decorators.verboser
def threadFunc_terminateFromSTDOUT(pipe: typing.IO, terminatoryWords: typing.Tuple[str,...]) -> None:
	while not constants.stop_flag.is_set():
		line = pipe.readline()
		if line:
			if any((killPhrase.encode() in line.strip() for killPhrase in terminatoryWords)):
				pidPrint(f"threadFunc_terminateFromSTDOUT for {pipe}: killPhrase detected: {line}! Terminating the program in 0.25 s!!!")
				sleep(0.25)
				constants.stop_flag.set()
				break

		else: break
		sleep(0.1)

	pipe.close()

def threadFunc_terminateTimeout(timeoutSeconds: float) -> None:
	pidPrint(f"threadFunc_terminateTimeout: {timeoutSeconds} seconds passed! Terminating the program in 0.25 s!!!")
	sleep(0.25)
	constants.stop_flag.set()
