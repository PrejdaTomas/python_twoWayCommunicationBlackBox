from AA_dependencies import pidPrint
from AA_dependencies import constants
from AA_dependencies import types
from AA_dependencies import signal
from AA_dependencies import sleep

#class Signals(IntEnum):
#	SIGABRT = 6
#	SIGFPE = 8
#	SIGILL = 4
#	SIGINT = 2
#	SIGSEGV = 11
#	SIGTERM = 15

def signal_handler(sig: int, frame: types.FrameType | None) -> None:
	constants.stop_flag.set()
	pidPrint("Signal handler: KeyboardInterrupt caught, setting stop flag.")

signal.signal(signalnum=signal.SIGINT, handler=signal_handler)
