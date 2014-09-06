import argparse
import configparser
import getpass
import logging
import os
import re
import sys
if sys.version_info < (3, 4):
    raise "This requires Python 3.4 or later"

kDevPrj = '/tmp/.devprj_{0}'.format(getpass.getuser())

logger = None
args = None

class Project(object):
    """This class is a simple container for a project."""

    def __init__(self, fullpath, vcs):
        index = fullpath.rfind(os.sep)
        if index < 0:
            raise Exception('No separator?')
        self.name = fullpath[index+1:]
        self.path = fullpath
        self.vcs = vcs

    def __lt__(self, other):
        if self.name != other.name:
            return self.name < other.name
        else:
            return self.path < other.path

    def __str__(self):
        return '{0} [{1}] {2}'.format(self.name, self.vcs, self.path)


def main():
    # if user wants the last one, exit now
    if args.last:
        sys.exit(0)

    # parse the configuration file
    config = configparser.RawConfigParser()
    config.read(args.conf)

    # get, expand, and check project root directories
    roots = config.get('devsearch', 'root').split(os.pathsep)
    logger.debug('root={0}'.format(roots))
    roots = [full_expand(root) for root in roots]
    for root in roots:
        if not os.path.isdir(root):
            logger.error('\'{0}\' is not a valid directory'
                         .format(root))
            sys.exit(-1)

    # get and check VCSs
    vcss = config.get('devsearch', 'vcs').split(os.pathsep)
    logger.debug('vcs={0}'.format(vcss))
    for vcs in vcss:
        if not vcs in kSupportedVcss:
            logger.error('\'{0}\' is not a supported version control system'
                         .format(vcs))
            logger.error('options are: {0}'.format(','.join(kSupportedVcss)))
            sys.exit(-1)

    # compile regex
    try:
        regex = re.compile(args.project)
        args.project = regex
    except:
        logger.error('invalid regular expression: {0}'.format(args.project))
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

    # apply search function
    logger.debug('Filtering:')
    filtered = []
    for project in projects:
        if (args.project.search(project.path) or
            args.project.search(project.vcs)):
            filtered.append(project)
            logger.debug('{0} passed'.format(project))
        else:
            logger.debug('{0} failed'.format(project))

    # print all projects for debug mode
    logger.debug('Filtered Projects:')
    for index, project in enumerate(filtered):
        logging.debug('{0}: {1}'.format(index + 1, project))

    # if no matches were found, exit
    if len(filtered) == 0:
        print('no project matches found')
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
    for index, project in enumerate(filtered):
        index_str = str(index + 1)
        if len(index_str) > max_index:
            max_index = len(index_str)
        if len(project.name) > max_name:
            max_name = len(project.name)
        if len(project.vcs) > max_vcs:
            max_vcs = len(project.vcs)
    logger.debug('{0} {1} {2}'.format(max_index, max_name, max_vcs))

    # print the projects nicely
    for index, project in enumerate(filtered):
        index_str = str(index + 1)
        print('{0}{1} : '
              .format(index_str, ' ' * (max_index - len(index_str))),
              end='')
        print('{0}{1} '
              .format(project.name, ' ' * (max_name - len(project.name))),
              end='')
        print('[{0}]{1} '
              .format(project.vcs, ' ' * (max_vcs - len(project.vcs))),
              end='')
        print('{0}'.format(project.path))

    # if user only wants to view projects, exit now
    if args.show:
        sys.exit(1)

    # get user's project selection
    selection = input('select a project: ')
    logger.debug('selection = {0}'.format(selection))
    good = False
    try:
        selection = int(selection)
        good = selection >= 1 and selection <= len(filtered)
    except ValueError:
        # if specifier wasn't an integer, try matching on text
        for index, project in enumerate(filtered):
            if project.name == selection:
                selection = index + 1
                good = True
                break
    # display error message if needed
    if not good:
        print('invalid project name or index: {0}'.format(selection))
        sys.exit(-1)

    # use selected project
    used = use_project(filtered[selection - 1])
    sys.exit(0 if used else 1)


def find_projects(dir_path, supported_vcss):
    projects = set()
    vcs = vcs_type(dir_path, supported_vcss)
    if vcs:
        logging.debug('found {0} project at {1}'.format(vcs, dir_path))
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


def full_expand(path):
    return os.path.abspath(os.path.expanduser(path))


def use_project(project):
    if args.show or logger.isEnabledFor(logging.DEBUG):
        print(project)
    if not args.show:
        with open(os.path.expanduser(kDevPrj), 'w') as fd:
            fd.write('{0}\n'.format(project.path))
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
    parser.add_argument('-s', '--show', action='store_true',
                        help='show project(s) but don\'t change directory')
    parser.add_argument('-l', '--last', action='store_true',
                        help='loads the last project used')
    parser.add_argument('-c', '--conf', default='~/.devconf',
                        type=check_conf_file,
                        help='configuration file to use')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print lots of useless stuff to the console')
    parser.add_argument('project', default='', nargs='?',
                        help='project search text (regex)')
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
    except KeyboardInterrupt:
        print()
        sys.exit(-1)
