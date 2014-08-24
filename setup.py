import distutils.core
#import codecs
import re
#import os
import sys

#def find_version(*file_paths):
#    version_file = codecs.open(os.path.join(os.path.abspath(
#        os.path.dirname(__file__)), *file_paths), 'r').read()
#    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
#                              version_file, re.M)
#    if version_match:
#        return version_match.group(1)
#    raise RuntimeError("Unable to find version string.")

def main():
  distutils.core.setup(
    name='devsearch',
    version='0.1.0',
    description='A project search and goto system.',
    author='Nic McDonald',
    author_email='nicci02@hotmail.com',
    license='None yet',
    packages=['devsearch'],
    scripts=['bin/devsearch'])

  # check whether the user has a source to devsearch in their ~/.bashrc
  src_re = re.compile(r'source\s*devsearch')
  try:
    with open('~/.bashrc', 'r') as fd:
      text = fd.read()
    if src_re.search(text):
      return 0
  except:
    pass
  print(('Please add the following line to your ~/.bashrc file:\n'
         '\talias dev=\'source devsearch\''))



if __name__ == '__main__':
  sys.exit(main())
