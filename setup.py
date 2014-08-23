import codecs
import re
import os
import sys

try:
  from setuptools import setup
except:
  print('please install setuptools:')
  print('  pip install setuptools')
  sys.exit(-1)

def find_version(*file_paths):
    version_file = codecs.open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), *file_paths), 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def main():
  try:
    setup(
      name='devsearch',
      version=find_version('devsearch', '__init__.py'),
      description='A project search and goto system.',
      author='Nic McDonald',
      author_email='nicci02@hotmail.com',
      license='None yet',
      packages=['devsearch'],
      scripts=['bin/devsearch'],
      install_requires=['termcolor >= 1.1.0']
    )
  except:
    return -1

  # check whether the user has a source to devsearch in their ~/.bashrc
  src_re = re.compile(r'source\s*devsearch')
  try:
    with open('~/.bashrc', 'r') as fd:
      text = fd.read()
  if not src_re.search(text):
    print(('Please add the following line to your ~/.bashrc file:\n'
           '\talias dev=\'source devsearch\''))


if __name__ == '__main__':
  sys.exit(main())
