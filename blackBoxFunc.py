from AA_dependencies import typing
from AA_dependencies import argparse
from AA_dependencies import Path
from AA_dependencies import os
from AA_dependencies import random
from AA_dependencies import pidPrint
from AA_dependencies import sleep, perf_counter
from AA_dependencies import AC_decorators

from main import constants

T = typing.TypeVar("T", str,None)



@AC_decorators.checkTypesAtCorrespondingIndices(inputTypes=(Path,), argumentPositions=(0,))
@AC_decorators.verboser
def writeSomething(targetPath: Path) -> None:
	t0 = perf_counter()

	pidPrint(f"writeSomething: trying to delete the output file {targetPath} from the last run")
	if os.path.exists(targetPath): os.remove(path=targetPath)
 
	pidPrint(f"writeSomething: trying to open a writePort to {targetPath}")
	with open(targetPath, "a") as writePort:
		pidPrint("writeSomething: writePort is open!")
		iterNumber = 0
		while not constants.stop_flag.is_set():
			genNumber	= random.randint(-500, +500)
			positive	= genNumber >= 0
			now			= f"{(round(perf_counter() - t0,2)):.2F}"
			pre, post 	= now.split(".")
			pre 		= pre.rjust(5, "0")
			post		= post.ljust(6, "0")
		
			now 		= ".".join((pre, post))
			consoleOutpt= f"---> {str(iterNumber).zfill(5)}:\t{now} s"

			if (iterNumber % 25 == 0): pidPrint(consoleOutpt)

			genNumber	= f"+{str(genNumber).rjust(3, '0')}" if positive else f"-{str(genNumber)[1:].rjust(3, '0')}"

			writePort.write(f"{now}\t{genNumber}\n")
			writePort.flush()
			sleep(0.1)
			iterNumber += 1
		pidPrint(f"writeSomething: trying to close a writePort to {targetPath}")
	pidPrint(f"writeSomething: writePort to {targetPath} is closed!")
	return

pidPrint("Starting blackBoxFunc.py")
parser = argparse.ArgumentParser(description="TUI")
parser.add_argument('output', type=str, help='Output file')
args = parser.parse_args()

path = Path(args.output)
writeSomething(targetPath=path)