from AA_dependencies import typing
from AA_dependencies import os
from AA_dependencies import subprocess
from AA_dependencies import threading
from AA_dependencies import psutil
from AA_dependencies import Path
from AA_dependencies import sleep

from AA_dependencies import AC_decorators
from AA_dependencies import pidPrint
from AA_dependencies import constants

import AE_listeners
import AF_terminators
import types

@AC_decorators.verboser
@AC_decorators.checkTypesAtCorrespondingIndices(inputTypes=(Path, list,), argumentPositions=(1, 3,))
def runner(	command: str,
			outFile: typing.Optional[typing.Union[None, Path]] = None,
			shell: typing.Optional[bool] = False,
			killPhrases: typing.List[typing.Union[None, str]] = None,
			timeOutInterval: typing.Optional[float] = 10.0,
	) -> typing.Tuple[int, subprocess.Popen, threading.Thread, threading.Thread, threading.Thread, threading.Timer]:
	pid 							= os.getpid()
	proc: subprocess.Popen			= subprocess.Popen(	command if shell else command.split(),
														stdout=	subprocess.PIPE,
														stdin=	subprocess.PIPE,
														stderr=	subprocess.PIPE,
														shell=	shell,
														cwd=	os.getcwd(),
														text=	True,
	)
	pidPrint(f"runner: current PPID = {os.getppid()}")
	pidPrint(f"runner: current PID  = {pid}")
	pidPrint(f"runner: proc PID     = {proc.pid}")
	pidPrint(f"runner: proc PPID    = {psutil.Process(pid=proc.pid).ppid()}")

	stdout_thread	= threading.Thread(target=AE_listeners.threadFunc_listenToSTDOUT,		args=(proc.stdout, ))
	stderr_thread	= threading.Thread(target=AE_listeners.threadFunc_listenToSTDOUT,		args=(proc.stderr, ))
	outfile_thread	= threading.Thread(target=AF_terminators.threadFunc_terminateFromFile,	args=(outFile, killPhrases, ))
	timer_thread	= threading.Timer(interval=timeOutInterval, function=AF_terminators.threadFunc_terminateTimeout, args=(timeOutInterval,))

	stdout_thread.start()
	stderr_thread.start()
	outfile_thread.start()
	timer_thread.start()
 
	stdout_thread.join()
	stderr_thread.join()
	outfile_thread.join()
	timer_thread.join()
 
	return pid, proc, stdout_thread, stderr_thread, outfile_thread, timer_thread
