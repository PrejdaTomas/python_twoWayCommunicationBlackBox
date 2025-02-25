Creates a two way communication between the Python process launching a black box function (might be an executable) launched from terminal. The function/exe must output a text file.
The processes are shut down after
1) timeout
2) kill phrases found in the output file
3) executable finishes

The output file is continually scanned in binary mode for speed.
Uses threads.

dependencies:
- Python 3.10.2 and its standard library
- os
- typing
- types
- functools
- random
- argparse
- datetime
- time
- subprocess
- threading
- psutil
- signal
- watchdog (not used yet)
