from AA_dependencies import threading
from AA_dependencies import multiprocessing
from AA_dependencies import functools
from AA_dependencies import typing
from AA_dependencies import psutil
from AA_dependencies import Path
from AA_dependencies import os
from AA_dependencies import pidPrint
from AA_dependencies import perf_counter, datetime
from AA_dependencies import constants
from AA_dependencies import AB_logging
from AA_dependencies import AC_signals
from AA_dependencies import getCPU
from AA_dependencies import cpu_info
from AA_dependencies import subprocess

F = typing.TypeVar('F', bound=typing.Callable[..., str])  # F is a callable that returns a str


def checkSequence(inputSequence: typing.Sequence) -> bool:
	return (isinstance(inputSequence, typing.Sequence) and not isinstance(inputSequence, str))

def checkTypesAtCorrespondingIndices(
				inputTypes: typing.Tuple[typing.Type,...],
				argumentPositions: typing.Tuple[int,...]
	) -> F:

	def decorator(funcToExecute: typing.Optional[typing.Callable[[F], F]]= None) -> F:
		@functools.wraps(wrapped=funcToExecute)
		def innerFunc(*args, **kwargs) -> F:
			if not checkSequence(inputSequence=inputTypes):
				constants.stop_flag.set()
				raise TypeError(f"checkTypesAtCorrespondingIndices for {funcToExecute.__name__}: the inputTypes must be a sequence of types, you've passed in: {inputTypes} : {type(inputTypes)}.")

			if isinstance(inputTypes, typing.Sequence):
				if any((not isinstance(typeV, typing.Type) for typeV in inputTypes)):
					constants.stop_flag.set()
					raise TypeError(f"checkTypesAtCorrespondingIndices for {funcToExecute.__name__}: inputTypes: one or more of the inputTypes are not a type, you've passed in: {inputTypes} : {type(inputTypes)}.")


			if not checkSequence(inputSequence=argumentPositions):
				constants.stop_flag.set()
				raise TypeError(f"checkTypesAtCorrespondingIndices for {funcToExecute.__name__}: argumentPositions must be a sequence of ints, you've passed in:{argumentPositions} : {type(argumentPositions)}.")

			if isinstance(argumentPositions, typing.Sequence):
				if any((not isinstance(index, int) for index in argumentPositions)):
					constants.stop_flag.set()
					raise TypeError(f"checkTypesAtCorrespondingIndices for {funcToExecute.__name__}: argumentPositions: one or more of indices are not an instance of an integer, you've passed in: {argumentPositions} : {type(argumentPositions)}!")

			if len(inputTypes) != len(argumentPositions):
				constants.stop_flag.set()
				raise ValueError(f"checkTypesAtCorrespondingIndices for {funcToExecute.__name__}: mismatch of count inputTypes ({len(inputTypes)}) and argumentPositions ({len(argumentPositions)}).")
			
			for typeV,index in zip(inputTypes, argumentPositions):
				argType = f"{list(kwargs.values())[index]}: {type(list(kwargs.values())[index])}"
				if not isinstance(list(kwargs.values())[index], typeV):
					constants.stop_flag.set()
					raise TypeError(f"checkTypesAtCorrespondingIndices for {funcToExecute.__name__}: the argument <{index}> is not an instance of {typeV.__name__}, you've passed in {argType}!")	
	
 
			returnValue = funcToExecute(*args, **kwargs)
			return returnValue
		return innerFunc

	return decorator

def verboser(iptFunc:typing.Optional[typing.Callable[[F], F]]= None) -> F:

	@functools.wraps(wrapped=iptFunc)
	def inner(*args, **kwargs) -> F:
		
		AB_logging.logging.info(f"{iptFunc.__name__}: starting execution at @ {datetime.now()} with the following arguments:")
		AB_logging.logging.info(f"\twith the following arguments:")
		for arg in args:AB_logging.logging.info(f"\t\t{iptFunc.__name__}: {arg}\t{type(arg)}")

		AB_logging.logging.info(f"\t{iptFunc.__name__}: with the following keyword arguments:")
		for kwarg,value in kwargs.items():AB_logging.logging.info(f"\t\t{iptFunc.__name__}: {kwarg.ljust(12, ' ')}=\t{value}\t{type(value)}")

		start_timer		= perf_counter()
		returnValue		= iptFunc(*args, **kwargs)
		executionTime	= perf_counter() - start_timer
		AB_logging.logging.info(f"{iptFunc.__name__}: finished execution at @ {datetime.now()}, took {executionTime} s.")
		#AB_logging.logging.info(f"{iptFunc.__name__}: returnValue = {returnValue}: {type(returnValue)}.\n")
		return returnValue
	return inner


import AE_IO
def threadLogger(iptFunc:typing.Optional[typing.Callable[[F], F]]= None) -> F:
	@functools.wraps(wrapped= iptFunc)
	def inner(*args, **kwargs) -> F:
		threadName			= f"001_{multiprocessing.current_process().pid}_{threading.current_thread().name}"
		thread_log_handler	= AB_logging.start_thread_logging(threadLoggerName=threadName)
		pidPrint(f"Logger {iptFunc.__name__}: START")

		returnVal			= iptFunc(*args, **kwargs)
		AB_logging.stop_thread_logging(log_handler=thread_log_handler)
		pidPrint(f"Logger {iptFunc.__name__}: END")

		return returnVal
	return inner



def parallelThreadedProcessWatchdog(	
			outFile:					typing.Optional[typing.Union[None, Path]]	= None,
			killPhrases:				typing.List[typing.Union[None, str]]		= None,
			timeOutInterval:			typing.Optional[typing.Union[None, float]]	= 10.0,
			waitTillTerminationPeriod:	typing.Optional[float]						= 0.05
	
	) ->F:

	def decorator(funcToExecute: typing.Optional[typing.Callable[[F], subprocess.Popen]]= None) -> F:
		import AG_terminators

		@functools.wraps(wrapped=funcToExecute)
		def innerFunc(*args, **kwargs) -> F:
			PID 							= os.getpid()
			sPID 							= str(PID).zfill(7)
			CPUInfo 						= cpu_info()
			CPU								= getCPU()
			sCPU							= str(CPU).zfill(3)

			now					= datetime.now()
			date				= "_".join(
				(	"".join(str(i).zfill(2) for i in (now.timetuple()[0:3])),
					"".join(str(i).zfill(2) for i in (now.timetuple()[3:6])))
			)	#yyyymmdd_hhmmss
			consoleProcess 		= funcToExecute(*args, **kwargs)

			stdout_thread	= None
			stderr_thread	= None
			outfile_thread	= None
			timer_thread	= None

			if not killPhrases is None:	
				stdout_thread		= threading.Thread(target=AG_terminators.terminateFromPIPE,	args=(consoleProcess.stdout, killPhrases, waitTillTerminationPeriod))
				stdout_thread.name	= f"p{sCPU}-t00-STDOUT-{date}"

				stderr_thread		= threading.Thread(target=AG_terminators.terminateFromPIPE,	args=(consoleProcess.stderr, killPhrases, waitTillTerminationPeriod))
				stderr_thread.name	= f"p{sCPU}-t01-STDERR-{date}"

				if not outFile is None:
					outfile_thread		= threading.Thread(target=AG_terminators.terminateFromFile,	args=(outFile, killPhrases, waitTillTerminationPeriod))
					outfile_thread.name	= f"p{sCPU}-t02-OUTFILE-{date}"

			if not timeOutInterval is None:
				timer_thread		= threading.Thread(target=AG_terminators.terminateTimeout,	args=(timeOutInterval, waitTillTerminationPeriod))
				timer_thread.name	= f"p{sCPU}-t03-TIMER-{date}"

			AB_logging.logging.info(f"runner: current PPID = {os.getppid()}")
			AB_logging.logging.info(f"runner: current PID  = {PID}")
			AB_logging.logging.info(f"runner: proc PID     = {consoleProcess.pid}")
			AB_logging.logging.info(f"runner: proc PPID    = {psutil.Process(pid=consoleProcess.pid).ppid()}")

			threads = filter(
				lambda x: x is not None,
				(stdout_thread, stderr_thread, outfile_thread, timer_thread)
			)

			for t in threads: t.start()
			for t in threads: t.join()

			consoleProcess.terminate()
			return consoleProcess

		return innerFunc

	return decorator