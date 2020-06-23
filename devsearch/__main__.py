"""
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

import argparse
import configparser
import getpass
import logging
import os
import re
import sys
import subprocess
import termcolor

if sys.version_info < (3, 4):
  raise "This requires Python 3.4 or later"

kDevPrj = '/tmp/.devprj_{0}'.format(getpass.getuser())

kRealHome = os.path.expanduser(os.getenv('HOME'))
kShortHome = '~'

logger = None
args = None

class Project(object):
  """This class is a simple container for a project."""

  def __init__(self, fullpath, vcs):
    index = fullpath.rfind(os.sep)
    if index < 0:
      raise Exception('No separator?')
    self.name = fullpath[index+1:]
    self.realpath = fullpath
    self.shortpath = fullpath.replace(kRealHome, kShortHome)
    self.vcs = vcs
    self.vcs_color = None
    if args.status:
      self.vcs_color = project_status(fullpath, vcs)
    self.status = None

  def __lt__(self, other):
    if self.name != other.name:
      return self.name < other.name
    else:
      return self.realpath < other.realpath

  def __str__(self):
    return '{0} [{1}] {2}'.format(self.name, self.vcs, self.shortpath)


def main():
  # if user wants the last one, exit now
  if args.previous:
    sys.exit(0)

  # parse the configuration file
  config = configparser.RawConfigParser()
  config.read(args.conf)

  # get, expand, and check project root directories
  roots = config.get('devsearch', 'root').split(os.pathsep)
  # ignore empty values, expand
  roots = [full_expand(root) for root in roots if root]
  logger.debug('root={0}'.format(roots))
  for root in roots:
    if not os.path.isdir(root):
      logger.error('\'{0}\' is not a valid directory'
                   .format(root))
      sys.exit(-1)

  # get and check VCSs
  vcss = config.get('devsearch', 'vcs').split(os.pathsep)
  vcss = [vcs for vcs in vcss if vcs]  # ignore empty values
  logger.debug('vcs={0}'.format(vcss))
  for vcs in vcss:
    if not vcs in kSupportedVcss:
      logger.error('\'{0}\' is not a supported version control system'
                   .format(vcs))
      logger.error('options are: {0}'.format(','.join(kSupportedVcss)))
      sys.exit(-1)

  # search for all projects
  projects = set()
  for root in roots:
    projects.update(find_projects(root, vcss))
  projects = list(projects)
  projects.sort()

  # print all projects for debug mode
  logger.debug('All Projects:')
  for idx, project in enumerate(projects):
    logger.debug('{0}: {1}'.format(idx+1, project))

  # now loop forever until done
  while True:
    # compile regex
    try:
      logger.debug('project regex: {0}'.format(args.project))
      args.project = re.compile(args.project)
    except:
      logger.error('invalid regular expression: {0}'.format(args.project))
      sys.exit(-1)

    # apply search function
    logger.debug('Filtering:')
    filtered = []
    for project in projects:
      if (args.project.search(project.realpath) or
          args.project.search(project.vcs)):
        filtered.append(project)
        logger.debug('{0} passed'.format(project))
      else:
        logger.debug('{0} failed'.format(project))

    # print all projects for debug mode
    logger.debug('Filtered Projects:')
    for index, project in enumerate(filtered):
      logger.debug('{0}: {1}'.format(index + 1, project))

    # if no matches were found, exit
    if len(filtered) == 0:
      print('no projects found')
      sys.exit(-1)

    # if one match was found, use it
    if len(filtered) == 1:
      used = use_project(filtered[0])
      sys.exit(0 if used else 1)

    # multiple matches were found
    # find widths in order to make nice columns
    max_index = 0
    max_name = 0
    max_vcs = 0
    max_path = 0
    for index, project in enumerate(filtered):
      index_str = str(index + 1)
      if len(index_str) > max_index:
        max_index = len(index_str)
      if len(project.name) > max_name:
        max_name = len(project.name)
      if len(project.vcs) > max_vcs:
        max_vcs = len(project.vcs)
      if len(project.shortpath) > max_path:
        max_path = len(project.shortpath)
    logger.debug('column widths: {0} {1} {2} {3}'
                 .format(max_index, max_name, max_vcs, max_path))

    # print the projects nicely
    for index, project in enumerate(filtered):
      # print the project index
      index_str = str(index + 1)
      print('{0}{1} : '
            .format(index_str, ' ' * (max_index - len(index_str))),
            end='')

      # print the project name
      print('{0}{1} '
            .format(project.name, ' ' * (max_name - len(project.name))),
            end='')

      # print the project VCS type (optionally show status via color)
      vcs = project.vcs
      if project.vcs_color:
        vcs = termcolor.colored(vcs, project.vcs_color, attrs=['bold'])
      print('[{0}]{1} '
            .format(vcs, ' ' * (max_vcs - len(project.vcs))),
            end='')

      # print the short path version of the project path
      print('{0}{1} '
            .format(project.shortpath,
                    ' ' * (max_path - len(project.shortpath))),
            end='')

      # FUTURE FEATURE - print the project status
      if project.status:
        print(project.status, end='')

      # end the line
      print()

    # try to interpret the project selection as an integer
    selection = input('selection: ')
    logger.debug('selection = {0}'.format(selection))
    good = False
    try:
      selection_index = int(selection)
      good = selection_index >= 1 and selection_index <= len(filtered)
      if good:
        selection = selection_index
    except ValueError:
      pass
    if good:
      used = use_project(filtered[selection - 1])
      sys.exit(0 if used else 1)

    # specifier wasn't a valid index, consider it a new regex
    args.project = selection
    projects = list(filtered)
    projects.sort()


def find_projects(dir_path, supported_vcss):
  projects = set()
  vcs = vcs_type(dir_path, supported_vcss)
  if vcs:
    logger.debug('found {0} project at {1}'.format(vcs, dir_path))
    projects.add(Project(dir_path, vcs))
  else:
    try:
      for dir_item in os.listdir(dir_path):
        full = os.path.join(dir_path, dir_item)
        if os.path.isdir(full):
          projects.update(find_projects(full, supported_vcss))
    except OSError:
      pass
  return projects


kSupportedVcss = ['git', 'svn', 'hg', 'cvs']
def vcs_type(path, supported):
  is_cnt = 0
  is_git = is_svn = is_hg = is_cvs = False

  if ('git' in supported and
      os.path.isdir(os.path.join(path, '.git'))):
    is_cnt += 1
    is_git = True
  if ('svn' in supported and
      os.path.isdir(os.path.join(path, '.svn'))):
    is_cnt += 1
    is_svn = True
  if ('hg' in supported and
      os.path.isdir(os.path.join(path, '.hg'))):
    is_cnt += 1
    is_hg = True
  if ('cvs' in supported and
      os.path.isdir(os.path.join(path, 'CVS'))):
    is_cnt += 1
    is_cvs = True

  if is_cnt == 0:
    return None
  elif is_cnt == 1:
    if is_git:
      return 'git'
    elif is_svn:
      return 'svn'
    elif is_hg:
      return 'hg'
    elif is_cvs:
      return 'cvs'
    else:
      logger.error('devsearch programmer is an idiot')
      sys.exit(-1)
  else:
    logger.error('{0} appears to be multiple VCS types ?!?!'
                 .format(path))
    sys.exit(-1)


def tryit(cwd, cmd):
  try:
    subprocess.check_call(cmd, cwd=cwd, shell=True)
    return True
  except:
    return False


def project_status(path, vcs):
  if vcs != 'git':
    return None

  if not tryit(path, 'git diff-files --quiet'):
    logger.debug('{0} is red'.format(path))
    return 'red'
  elif not tryit(path, 'git diff-index --quiet --cached HEAD'):
    logger.debug('{0} is yellow'.format(path))
    return 'yellow'
  else:
    logger.debug('{0} is green'.format(path))
    return 'green'

  """ FUTURE WORK - show status text
  proc = subprocess.Popen('git status', cwd=path,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          shell=True)
  stdout, stderr = proc.communicate()
  retcode = proc.returncode
  if retcode != 0:
    print('git status failed for {0}'.format(path))
    sys.exit(-1)
  stdout = stdout.decode('utf-8')

  is_up_to_date = stdout.find('Your branch is up-to-date with') >= 0
  is_ahead = stdout.find('Your branch is ahead of') >= 0
  assert is_up_to_date or is_ahead
  assert not (is_up_to_date and is_ahead)
  has_untracked = stdout.find('Untracked files:') >= 0
  needs_commit = stdout.find('Changes to be committed:') >= 0

  if is_up_to_date:
    status = 'UpToDate'
  else:
    status = 'Ahead'
  if needs_commit:
    status += '-NeedsCommit'
  if has_untracked:
    status += '-Untracked'
  """


def full_expand(path):
  return os.path.abspath(os.path.expanduser(path))


def use_project(project):
  if args.list or logger.isEnabledFor(logging.DEBUG):
    print(project)
  if not args.list:
    with open(os.path.expanduser(kDevPrj), 'w') as fd:
      fd.write('{0}\n'.format(project.realpath))
      logger.debug('wrote path to {0}'.format(kDevPrj))
    return True
  else:
    return False


def check_conf_file(val):
  val = os.path.abspath(os.path.expanduser(val))
  if not os.path.isfile(val):
    raise argparse.ArgumentTypeError('{0} doesn\'t exist'.format(val))
  if not os.access(val, os.R_OK):
    raise argparse.ArgumentTypeError('{0} isn\'t readable'.format(val))
  return val


if __name__ == '__main__':
  desc = 'Go to your development project via intuitive search'
  parser = argparse.ArgumentParser(prog='devsearch', description=desc)
  parser.add_argument('-s', '--status', action='store_true',
                      help='show the status of the project (git only)')
  parser.add_argument('-l', '--list', action='store_true',
                      help='list project(s) but don\'t change directory')
  parser.add_argument('-p', '--previous', action='store_true',
                      help='loads the previous project used')
  parser.add_argument('-c', '--conf', default='~/.devsearchrc',
                      type=check_conf_file,
                      help='configuration file to use')
  parser.add_argument('-d', '--debug', action='store_true',
                      help='print lots of useless stuff to the console')
  parser.add_argument('project', default='', nargs='?',
                      help='project search regex')
  try:
    args = parser.parse_args()
  except SystemExit:
    sys.exit(-1)

  # create a logger
  logger = logging.getLogger()
  logger.addHandler(logging.StreamHandler(stream=sys.stdout))
  if args.debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)
  logger.debug('args={0}'.format(args))

  try:
    sys.exit(main())
  except (KeyboardInterrupt, EOFError):
    print()
    sys.exit(-1)
