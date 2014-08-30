# check python version
import sys
if sys.version_info < (3, 3):
    raise "This requires Python 3.3 or later"
