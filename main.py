import timedFunc
from AC_decorators import verboser
from AG_runCommand import runner
from AA_dependencies import Path
from AA_dependencies import os
from AA_dependencies import random
from AA_dependencies import constants, subprocess,sleep
from AA_dependencies import threading, pidPrint


formattedNum = lambda genNumber: f"+{str(genNumber).rjust(3, '0')}" if genNumber >= 0 else f"-{str(genNumber)[1:].rjust(3, '0')}"

@verboser
def main(outputFile: str = os.path.join(os.getcwd(), "outputFile.out")) -> tuple[int, subprocess.Popen, threading.Thread, threading.Thread, threading.Thread, threading.Timer]:
	pid, proc, thread_stdout, thread_stderr, thread_outFile, thread_timer = runner(
		command= f"del {outputFile} && python blackBoxFunc.py {outputFile}",
		outFile= Path(outputFile),
		shell= True,
		killPhrases=[formattedNum(random.randint(-500, 500)) for i in range(25)]
	)

	return pid, proc, thread_stdout, thread_stderr, thread_outFile, thread_timer

if __name__ == "__main__":
	constants.verbose = True
	main()
