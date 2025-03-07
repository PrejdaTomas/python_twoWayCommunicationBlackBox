from AA_dependencies import typing
from AA_dependencies import Path
from AA_dependencies import os
from AA_dependencies import pidPrint
from AA_dependencies import constants
from AA_dependencies import sleep
from AA_dependencies import threading
from AA_dependencies import AB_logging
from AA_dependencies import AC_signals
from AA_dependencies import AD_decorators
from AA_dependencies import AE_IO


@AD_decorators.threadLogger
@AD_decorators.verboser
def terminateFromFile(outFile: Path, terminatoryWords: typing.Tuple[str,...], waitTillTermination: typing.Optional[float] = 0.25) -> None:
	#killCondition: typing.Callable[[str,bytes], bool] = lambda killPhraseASCII,lineBINARY: any((killPhraseASCII.encode() in lineBINARY, constants.stop_flag.is_set()))
	AE_IO.waitTillFileExists_stupid(filePath=outFile,)

	with open(outFile, "rb") as readPort:
		terminated = False
		while not constants.stop_flag.is_set():
			if terminated: 
				AB_logging.logging.info(f"terminateFromFile for {outFile}: internal terminated flag set to True, shutting down")
				break

			if AE_IO.getFileSizeInBytesForAnConstantlyOpenedChangingFile(readPortInput=readPort) > 0:
				lines = AE_IO.readLastNLines(readPortInput=readPort, bufferSize=1024, numberOfLines=5)
				for line in lines:
					for killPhrase in terminatoryWords:
						if constants.stop_flag.is_set():
							AB_logging.logging.info(f"terminateFromFile for {outFile}: another process reached terminatory criteria, shutting down!")
							terminated = True
							break

						if killPhrase.encode() in line:
							AB_logging.logging.info(f"terminateFromFile for {outFile}: killPhrase detected: {killPhrase}: {line.strip()}, shutting down!")
							terminated = True
							sleep(waitTillTermination)
							constants.stop_flag.set()
							break
					if terminated: break
			else:
				AB_logging.logging.info(f"terminateFromFile for {outFile}: file size <= 0, probably corrupt, shutting down!")
				break
			sleep(0.1)


@AD_decorators.threadLogger
@AD_decorators.verboser
def terminateFromPIPE(pipe: typing.IO, terminatoryWords: typing.Tuple[str,...], waitTillTermination: typing.Optional[float] = 0.25) -> None:
	#killCondition: typing.Callable[[str,str], bool] = lambda killPhraseASCII,lineASCII: any((killPhraseASCII in lineASCII, constants.stop_flag.is_set()))

	terminated = False
	while not constants.stop_flag.is_set():
		if terminated: 
			AB_logging.logging.info(f"terminateFromPIPE for {pipe}: internal terminated flag set to True, shutting down!")
			break

		line = pipe.readline()
		if line:
			for killPhrase in terminatoryWords:
				if constants.stop_flag.is_set():
					AB_logging.logging.info(f"terminateFromPIPE for {pipe}: another process reached terminatory criteria, shutting down!")
					terminated = True
					break
 
				if killPhrase in line:
					AB_logging.logging.info(f"terminateFromPIPE for {pipe}: killPhrase detected: {killPhrase}: {line.strip()}, shutting down")
					terminated = True
					sleep(waitTillTermination)
					constants.stop_flag.set()
					break
			sleep(0.01)

		else:
			AB_logging.logging.info(f"terminateFromPIPE for {pipe}: line is None - EOF, shutting down!")
			break
	pipe.close()

@AD_decorators.threadLogger
@AD_decorators.verboser
def terminateTimeout(timeoutSeconds: float, waitTillTermination: typing.Optional[float] = 0.25) -> None:
	timeElapsed	= 0.0
	waitTime	= 0.1

	while timeElapsed < timeoutSeconds:
		if constants.stop_flag.is_set():
			AB_logging.logging.info(f"terminateTimeout: another process reached terminatory criteria, shutting down!")
			return
		sleep(waitTime)
		timeElapsed += waitTime

	AB_logging.logging.info(f"terminateTimeout: {timeoutSeconds} seconds passed, shutting down!")
	sleep(waitTillTermination)
	constants.stop_flag.set()


#Terminating the program in {waitTillTermination} s!

#def terminateFromFile(outFile: Path, terminatoryWords: typing.Tuple[str,...], waitTillTermination: typing.Optional[float] = 0.25) -> None: pass
#def terminateFromPIPE(pipe: typing.IO, terminatoryWords: typing.Tuple[str,...], waitTillTermination: typing.Optional[float] = 0.25) -> None: pass
#def terminateTimeout(timeoutSeconds: float, waitTillTermination: typing.Optional[float] = 0.25) -> None: pass
