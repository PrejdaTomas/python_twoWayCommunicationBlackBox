from AA_dependencies import typing
from AA_dependencies import os
from AA_dependencies import subprocess
from AA_dependencies import threading
from AA_dependencies import psutil
from AA_dependencies import Path
from AA_dependencies import sleep
from AA_dependencies import formattedNum
from AA_dependencies import random

from AA_dependencies import AB_logging
from AA_dependencies import AD_decorators
from AA_dependencies import pidPrint
from AA_dependencies import constants
from AA_dependencies import cpu_info
from AA_dependencies import getCPU

import AF_listeners
import AG_terminators
import types


@AD_decorators.verboser
@AD_decorators.checkTypesAtCorrespondingIndices(inputTypes=(Path, list,), argumentPositions=(1, 3,))
def runner(	command:					str,
			outFile:					typing.Optional[typing.Union[None, Path]]	= None,
			shell:						typing.Optional[bool]						= False,
			killPhrases:				typing.List[typing.Union[None, str]]		= None,
			timeOutInterval:			typing.Optional[float]						= 10.0,
			waitTillTerminationPeriod:	typing.Optional[float]						= 0.05
	
	) -> typing.Tuple[	int,
						subprocess.Popen,
						threading.Thread, threading.Thread, threading.Thread, threading.Thread
	]:

	PID 							= os.getpid()
	sPID 							= str(PID).zfill(7)
	CPUInfo 						= cpu_info()
	CPU								= getCPU()
	sCPU							= str(CPU).zfill(3)
 
	proc: subprocess.Popen			= subprocess.Popen(	command if shell else command.split(),
														stdout=	subprocess.PIPE,
														stdin=	subprocess.PIPE,
														stderr=	subprocess.PIPE,
														shell=	shell,
														cwd=	os.getcwd(),
														text=	True,
	)
	AB_logging.logging.info(f"runner: current PPID = {os.getppid()}")
	AB_logging.logging.info(f"runner: current PID  = {PID}")
	AB_logging.logging.info(f"runner: proc PID     = {proc.pid}")
	AB_logging.logging.info(f"runner: proc PPID    = {psutil.Process(pid=proc.pid).ppid()}")

	#stdout_thread	= threading.Thread(target=AE_listeners.listenToSTDOUT,		args=(proc.stdout, ))
	#stderr_thread	= threading.Thread(target=AE_listeners.listenToSTDOUT,		args=(proc.stderr, ))
	stdout_thread	= threading.Thread(target=AG_terminators.terminateFromPIPE,	args=(proc.stdout, killPhrases, waitTillTerminationPeriod))
	stdout_thread.name= f"p{sCPU}-t00-STDOUT"

	stderr_thread	= threading.Thread(target=AG_terminators.terminateFromPIPE,	args=(proc.stderr, killPhrases, waitTillTerminationPeriod))
	stderr_thread.name= f"p{sCPU}-t01-STDERR"

	outfile_thread	= threading.Thread(target=AG_terminators.terminateFromFile,	args=(outFile, killPhrases, waitTillTerminationPeriod))
	outfile_thread.name= f"p{sCPU}-t02-OUTFILE"

	timer_thread	= threading.Thread(target=AG_terminators.terminateTimeout,	args=(timeOutInterval, waitTillTerminationPeriod))
	timer_thread.name= f"p{sCPU}-t03-TIMER"

	
	threads = stdout_thread, stderr_thread, outfile_thread, timer_thread

	for t in threads: t.start()

	for t in threads: t.join()

	proc.terminate()
	return PID, proc, stdout_thread, stderr_thread, outfile_thread, timer_thread


@AD_decorators.verboser
def runner(	command:					str,
			shell:						typing.Optional[bool]	= False,
			stdin:						typing.Optional[int]	= subprocess.PIPE,
			stderr:						typing.Optional[int]	= subprocess.PIPE,
			stdout:						typing.Optional[int]	= subprocess.PIPE,
			currentWorkDir:				typing.Optional[Path]	= Path(value=os.getcwd()),
			text: 						typing.Optional[bool]	= True
	) -> subprocess.Popen:
	proc: subprocess.Popen			= subprocess.Popen(	command if shell else command.split(),
														stdin=	stdin,
														stdout=	stdout,
														stderr=	stderr,
														shell=	shell,
														cwd=	currentWorkDir,
														text=	text,
	)

	return proc

