import timedFunc
from AD_decorators import verboser
from AD_decorators import parallelThreadedProcessWatchdog
from AH_runCommand import runner
from AA_dependencies import Path
from AA_dependencies import os
from AA_dependencies import random
from AA_dependencies import constants, subprocess,sleep
from AA_dependencies import multiprocessing, threading, pidPrint

from AA_dependencies import AB_logging
from AA_dependencies import typing
formattedNum = lambda genNumber: f"+{str(genNumber).rjust(3, '0')}" if genNumber >= 0 else f"-{str(genNumber)[1:].rjust(3, '0')}"

  
@verboser
def _main(	outputFile: Path = Path("outputFile.out"),
			killPhrases=[formattedNum(random.randint(-500, 500)) for i in range(25)],
			timeOutInterval=10.0,
			waitTillTerminationPeriod= 0.0

) -> tuple[int, subprocess.Popen, threading.Thread, threading.Thread, threading.Thread, threading.Timer]:

	AB_logging.config_root_logger(globalLoggerName=f"001_{multiprocessing.current_process().pid}")
	@parallelThreadedProcessWatchdog(
		outFile=outputFile,
		killPhrases=killPhrases,
		timeOutInterval=timeOutInterval,
		waitTillTerminationPeriod=waitTillTerminationPeriod
	)
	
	def _tmpFunc() -> subprocess.Popen:
		if outputFile is None:
			if os.path.exists("outptt"): return runner(command= f"del outptt* && python blackBoxFunc.py {outputFile}",shell= True,)
			return runner(command= f"python blackBoxFunc.py {outputFile}",shell= True,)
		else:
			if os.path.exists(outputFile): return runner(command= f"del {outputFile} && python blackBoxFunc.py {outputFile}",shell= True,)
			return runner(command= f" python blackBoxFunc.py {outputFile}",shell= True,)

	proc = _tmpFunc()

	return proc

def main() -> None:
	AB_logging.config_root_logger(globalLoggerName="")
	AB_logging.logging.info("STARTING!")
	constants.verbose = False

	processes: list[multiprocessing.Process] = []
	for _ in range(16):
		AB_logging.logging.info(f"SPAWNING process ID: P{str(_).zfill(3)}")
		processes.append(multiprocessing.Process(target=_main, args=(Path(f"outputNew_{_}"), [formattedNum(random.randint(-500, 500)) for i in range(25)], None, 0.025), name=f"P{str(_).zfill(3)}"))

	for _ in processes:
		AB_logging.logging.info(f"STARTING process ID: P{str(_).zfill(3)}")
		_.start()
	
	for _ in processes:
		AB_logging.logging.info(f"JOINING process ID: P{str(_).zfill(3)}")
		_.join()
	#for _ in [nuProcess_1, nuProcess_2]: _.join()

	@verboser
	def _combineLogs() -> None: AB_logging.combineLogs()

	_combineLogs()
	AB_logging.logging.info("TERMINATING!")


if __name__ == "__main__":
	main()