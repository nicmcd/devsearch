import distutils.core
import re
import os
import sys

def main():
  distutils.core.setup(
    name='devsearch',
    version='0.2.0',
    description='A project search and goto system.',
    author='Nic McDonald',
    author_email='nicci02@hotmail.com',
    license='None yet',
    py_modules=['devsearch'],
    scripts=['bin/devsearch'])

  # check whether the user has a source to devsearch in their ~/.bashrc
  src_re = re.compile(r'source\s*devsearch')
  try:
    with open(os.path.expanduser('~/.bashrc'), 'r') as fd:
      text = fd.read()
    if src_re.search(text):
      return 0
  except IOError:
    pass
  print(('Please add the following line to your ~/.bashrc file:\n'
         '\talias dev=\'source devsearch\''))


if __name__ == '__main__':
  sys.exit(main())
