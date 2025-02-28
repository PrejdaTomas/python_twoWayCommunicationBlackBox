import typing, types
import os
import logging
import logging.config as loggingConfig

import functools
import random
import argparse
import platform

from datetime import datetime
from time import sleep, perf_counter
# import watchdog.events as watchdogEvents
# import watchdog.observers as watchdogObservers
import subprocess, threading, multiprocessing, psutil, signal


class Singleton:
	__instance: typing.Self = None
	def __new__(cls) -> typing.Self:
		if cls.__instance is None:
			nuInstance = super(Singleton, cls).__new__(cls)
			cls.__instance = nuInstance
		return cls.__instance
	
class Constants(Singleton):
	verbose: bool
	"""bool: toggles the stdout verbosity on/off. Defaults to True"""

	stop_flag: threading.Event
	"""threading.Event: set if ctrl-c pressed"""

	def __init__(self) -> None:
		super().__init__()
		self.verbose = True
		self.stop_flag = threading.Event()



constants = Constants()


class Path(str, os.PathLike):
	def __new__(cls, value: str) -> typing.Self:
		if len(value) > 260: raise ValueError(f"{cls.__name__}: {value} length exceeds 260 characters")
		return super(Path, cls).__new__(cls, value)

	def __setattr__(self, name: str, value: str) -> None:
		if not isinstance(value, str): raise TypeError("Value must be a string")
		if name == 'value' and len(value) > 260: raise ValueError(f"{self.__class__.__name__}: {value} length exceeds 260 characters")
		super().__setattr__(name, value)

	def __fspath__(self) -> str:
		return str(self)

def getConsoleOutput(*args: typing.Optional[str], sep: typing.Optional[str] = " ", end: typing.Optional[str] = "\n") -> str:
	"""Print the statement with process id added in front of the string, also returns the output.

	Args:
		*args (str): input statements
		sep (str): separator, defaults to ' '
		end (str): string ending, defaults to '\n'

	Returns:
		str: PID + input statements
	"""
	strInput = sep.join(map(str, args))
	returnVal: str = f"[PID_{str(os.getpid()).zfill(7)}]: {strInput}"
	returnVal = returnVal.expandtabs()
	returnVal = returnVal.strip()
	return returnVal

def cpu_info() -> str: 
	if platform.system() == 'Windows':  return platform.processor() 

	elif platform.system() == 'Darwin':
		command = '/usr/sbin/sysctl -n machdep.cpu.brand_string' 
		return os.popen(command).read().strip() 

	elif platform.system() == 'Linux': 
		command = 'cat /proc/cpuinfo' 
		return os.popen(command).read().strip()

	raise OSError('cpu_info: platform not identified.')


if platform.system() == "Windows":
	import ctypes

	def getCPU() -> typing.Union[int, None]:
		try:
			GetCurrentProcessorNumber = ctypes.windll.kernel32.GetCurrentProcessorNumber
			core_id		= GetCurrentProcessorNumber()
			return core_id
		except: return None


elif platform.system() == "Linux":
	def getCPU() -> typing.Union[int, None]:
		try:
			with open(f"/proc/{os.getpid()}/stat") as f:
				fields = f.read().split()
				core_id = int(fields[38])  # The 39th field is the core ID
			return core_id
		except: return None

def pidPrint(*args: typing.Optional[str], sep: typing.Optional[str] = " ", end: typing.Optional[str] = "\n") -> str:
	"""Print the statement with process id added in front of the string, also returns the output.

	Args:
		*args (str): input statements
		sep (str): separator, defaults to ' '
		end (str): string ending, defaults to '\n'

	Returns:
		str: PID + input statements
	"""
	returnVal = getConsoleOutput(*args, sep, end)
	if constants.verbose:
		print(returnVal, sep=sep, end=end, flush=True)
	return returnVal

import AB_logging
import AC_signals
import AD_decorators
import AE_IO