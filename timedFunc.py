from AA_dependencies import typing
from AA_dependencies import os
from AA_dependencies import sleep, perf_counter
from AA_dependencies import subprocess, threading, psutil
from AA_dependencies import constants
from AA_dependencies import pidPrint
from AA_dependencies import Path
from AC_decorators import checkTypesAtCorrespondingIndices

@checkTypesAtCorrespondingIndices(inputTypes=(Path,), argumentPositions=(1,))
def runWithTimeout(command: typing.Union[typing.List[str], str],
				   executableName: typing.Union[None, str],
				   timeoutSeconds: typing.Optional[float] = 15.0,
				   afterCompletionFunc: typing.Union[None, typing.Callable] = None,
				   outFilePath: typing.Optional[str] = None,
				   terminatoryWordsInOut: typing.Optional[typing.Union[None, str, typing.List[str]]] = None,
				   time_waitTillOutputfileCreated: typing.Optional[float] = 0.5,
				   time_periodicOutputfileCheck: typing.Optional[float] = 0.1,
				   functionExecutedBeforeProcessing: typing.Optional[typing.Union[None, typing.Callable]] = None,
				   shell: typing.Optional[bool] = False,) -> int:
	"""
	Run a command with a timeout.

	Args:

		- command (list[str] | str): A command line command.
		- executableName (str): File name of the launched child executable including suffix.
		- timeoutSeconds (float, optional): Time till the timed function terminates. Defaults to 15.0.
		- afterCompletionFunc (None | callable, optional): Function which executes after the timeout. Defaults to None.
		- outFilePath (None | str, optional): Path to the output file which will be spawned by the parent process launched child executable. Defaults to None.
		- terminatoryWordsInOut (None | str | list[str]): Phrases to watch out for in the output file to kill the process. Either nothing, or a single string phrase, or a list of string phrases. Defaults to None.
		- time_waitTillOutputfileCreated (float, optional): Time given to wait till the output file is first created (might be empty at this point). Defaults to 0.5.
		- time_periodicOutputfileCheck (float, optional): Interval at which the output file is checked for new content (the terminatory words). Defaults to 0.1.
		- functionExecutedBeforeProcessing (None | callable, optional): function (zero arguments, use functools.reduce or a lambda func) to be execute on startup. Defaults to None.
		- shell (bool, optional): If False, input format: ["word1", "-r", "argument"], if True, input format: "word1 -r argument". Defaults to False.

	Raises:
		TypeError: If the shell attribute is true and the command is not a string.

	Returns:
		int: Return code of the command.
	"""

	#region checks-1
	if not executableName is None:
		if not os.path.exists(executableName):
			raise FileNotFoundError(f"runWithTimeout: the inputted executableName does not exist: {executableName}")

	if shell and isinstance(command, list):
		raise TypeError("runWithTimeout: if the shell attribute is true, the command needs to be a string")
	#endregion checks-1
	if functionExecutedBeforeProcessing is not None:
		functionExecutedBeforeProcessing()
	startTime		= perf_counter()
	elapsedTime		= startTime
	proc			= subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=shell)
	timeout_event	= threading.Event()
 
	def _findPID_childProcess(PID_parentProcess: int) -> typing.Union[None, int]:
		if proc.poll() is not None:
			if constants.verbose: pidPrint(f"runWithTimeout: The parent is already dead: proc")
			return None

		parent = psutil.Process(pid=PID_parentProcess)
		if parent.is_running() is False:
			if constants.verbose: pidPrint(f"runWithTimeout: The parent is already dead: proc")
			return None

		children = parent.children(recursive=True)
		for child in children:
			if child.name() == executableName and parent.is_running() and proc.poll() is not None:
				if constants.verbose: pidPrint(f"runWithTimeout: Found parent for child {child.pid}: {child.name()} -> {parent.pid}: {parent.name()}")
				return child.pid
			else:
				if constants.verbose: pidPrint(f"runWithTimeout: The parent is already dead: proc")

		return None

	def _executeOnTimeout() -> None:
		nonlocal startTime, elapsedTime, timeout_event
		timeout_event.set()
		elapsedTime = perf_counter() - startTime
		child_pid = _findPID_childProcess(PID_parentProcess=proc.pid)
		if child_pid is not None:
			child_proc = psutil.Process(pid=child_pid)
			if constants.verbose: pidPrint(f"runWithTimeout: Terminating the child_proc: {child_pid}:{child_proc.name()}")
			child_proc.kill()
		proc.kill()

	def _monitorOutFile() -> None:
		nonlocal timeout_event, elapsedTime
		sleep(time_waitTillOutputfileCreated)  # Wait until the output file is created

		if not os.path.exists(outFilePath):
			raise FileNotFoundError(f"runWithTimeout: outFilePath does not exist: {outFilePath}, files: {os.listdir(os.getcwd())}!")

		if terminatoryWordsInOut is not None:
			if isinstance(terminatoryWordsInOut, str):
				binaryKeywords = [terminatoryWordsInOut.encode()]
			else:
				binaryKeywords = [word.encode() for word in terminatoryWordsInOut]

			with open(outFilePath, 'rb') as readPort:
				while not timeout_event.is_set():
					readPort.seek(0, os.SEEK_END)  # Move to the end of the file
					file_size = readPort.tell()
					if file_size > 0:
						readPort.seek(max(file_size - 1024, 0), os.SEEK_SET)  # Read the last 1KB of the file
						lines = readPort.readlines()[20:]
						if any(binaryWord in line for binaryWord in binaryKeywords for line in lines):
							if constants.verbose: pidPrint(f"runWithTimeout: terminatory word found")
							_executeOnTimeout()
							break
						if _findPID_childProcess(PID_parentProcess=proc.pid) is None:
							if constants.verbose: pidPrint(f"runWithTimeout: parent process is dead")
							_executeOnTimeout()
							break

					sleep(time_periodicOutputfileCheck)  # Adjust the interval as needed

	#region threads
	if isinstance(outFilePath, str):
		if isinstance(terminatoryWordsInOut, (type(None), str, list)):
			if isinstance(terminatoryWordsInOut, list):
				for word in terminatoryWordsInOut:
					if not isinstance(word, str):
						raise TypeError(f"runWithTimeout: one or more of the terminatoryWordsInOut is not a string: {word}: {type(word)}!")

			timer = threading.Timer(interval=timeoutSeconds, function=_executeOnTimeout)
			monitorThread = threading.Thread(target=_monitorOutFile)
		else:
			raise TypeError(f"runWithTimeout: the terminatoryWordsInOut is neither None, string or a list of strings: {terminatoryWordsInOut}: {type(terminatoryWordsInOut)}!")
	elif outFilePath is None:
		timer = threading.Timer(interval=timeoutSeconds, function=_executeOnTimeout)
		monitorThread = None
	else:
		raise TypeError(f"runWithTimeout: The outFilePath is neither a string nor None: {outFilePath}: {type(outFilePath)}")

	def _timedFunc() -> int:
		returnValFunctionAfter = None
		returnCode = 1
		try:
			timer.start()
			if monitorThread:
				if constants.verbose: pidPrint(f"runWithTimeout: starting a monitor")
				monitorThread.start()
			returnCode = proc.wait()
		finally:
			timer.cancel()
			if constants.verbose: pidPrint(f"runWithTimeout: stopped the timer")

			if timeout_event.is_set() and afterCompletionFunc is not None:
				returnValFunctionAfter = afterCompletionFunc()
				returnCode = -1

			if monitorThread: monitorThread.join()

		return returnCode
	if constants.verbose: pidPrint(f"runWithTimeout: succesfully terminated")
	return _timedFunc()

