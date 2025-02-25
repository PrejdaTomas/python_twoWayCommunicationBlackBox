import typing, types
import os


import functools
import random
import argparse
from datetime import datetime
from time import sleep, perf_counter
import watchdog.events as watchdogEvents
import watchdog.observers as watchdogObservers
import subprocess, threading, psutil, signal


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
		return str.__new__(cls, value)

	def __setattr__(self, name: str, value: str) -> None:
		if not isinstance(value, str): raise TypeError("Value must be a string")
		if name == 'value' and len(value) > 260: raise ValueError(f"{self.__class__.__name__}: {value} length exceeds 260 characters")
		super().__setattr__(name, value)

	def __fspath__(self) -> str:
		return str(self)


def pidPrint(*args: typing.Optional[str], sep: typing.Optional[str] = " ", end: typing.Optional[str] = "\n") -> str:
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
	if constants.verbose:
		print(returnVal, sep=sep, end=end, flush=True)
	return returnVal

import AB_signals
import AC_decorators
import AD_IO