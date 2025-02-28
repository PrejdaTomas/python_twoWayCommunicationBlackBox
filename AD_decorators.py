from AA_dependencies import threading
from AA_dependencies import functools
from AA_dependencies import typing
from AA_dependencies import Path
from AA_dependencies import os
from AA_dependencies import pidPrint
from AA_dependencies import perf_counter, datetime
from AA_dependencies import constants
from AA_dependencies import AB_logging
from AA_dependencies import AC_signals

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


def threadLogger(iptFunc:typing.Optional[typing.Callable[[F], F]]= None) -> F:

	@functools.wraps(wrapped= iptFunc)
	def inner(*args, **kwargs) -> F:
		threadName			= f"001_{threading.current_thread().name}"
		thread_log_handler	= AB_logging.start_thread_logging(threadLoggerName=threadName)
		pidPrint(f"Logger {iptFunc.__name__}: START")

		returnVal			= iptFunc(*args, **kwargs)
		AB_logging.stop_thread_logging(log_handler=thread_log_handler)
		pidPrint(f"Logger {iptFunc.__name__}: END")
		return returnVal
	return inner

