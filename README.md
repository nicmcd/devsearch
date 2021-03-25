# DevSearch

This project implements a simple system for finding a desired project to work on and changing the current directory to it.
This is really useful when you have lots of projects on your machine or when you use deep directory hierarchies.

## Usage
Simple example:
```bash
me@tux:~/$ dev linux
me@tux:~/projs/torvalds/linux$
```

If there is more than one match, an option list will be presented:
```bash
me@tux:~/$ dev linux
1 : linux [git] ~/projs/torvalds/linux
2 : linux [git] ~/projs/raspberrypi/linux
3 : linux [git] ~/projs/svenkatr/linux
selection: 2
me@tux:~/projs/raspberrypi/linux$
```

Regex's can be used:
```bash
me@tux:~/$ dev [s,S]im[0-9]+
1 : booksim2 [git] ~/projs/booksim/booksim2
2 : Sim2600  [git] ~/projs/gregjames/Sim2600
selection: 1
me@tux:~/projs/booksim/booksim2$
```
or
```bash
me@tux:~/$ dev google\|hplabs
1 : paramgmt  [git] ~/projs/google/paramgmt
2 : protobuf  [git] ~/projs/google/protobuf
3 : cacti     [git] ~/projs/hplabs/cacti
4 : mcpat     [git] ~/projs/hplabs/mcpat
5 : supersim  [git] ~/projs/hplabs/supersim
selection: cacti
me@tux:~/projs/hplabs/cacti
```

Searching is recursive:
```bash
me@tux:~/$ dev lib
1 : libjson         [git] ~/projs/vincenthz/libjson
2 : libjson-rpc-cpp [git] ~/projs/cinemast/libjson-rpc-cpp
3 : libevent        [git] ~/projs/nmathewson/libevent
4 : libevhtp        [git] ~/projs/ellzey/libevhtp
5 : zlib            [git] ~/projs/madler/zlib
selection: lib[a-z]+
1 : libjson         [git] ~/projs/vincenthz/libjson
2 : libjson-rpc-cpp [git] ~/projs/cinemast/libjson-rpc-cpp
3 : libevent        [git] ~/projs/nmathewson/libevent
4 : libevhtp        [git] ~/projs/ellzey/libevhtp
selection: event
me@tux:~/projs/nmathewson/libevent
```

## Installation
The `dev` command shown above is an alias which calls `source devsearch`. Add the following to your startup script (e.g., ~/.bashrc):
```bash
alias dev='source devsearch'
```

Installation of the `devsearch` program is done with pip:

```bash
pip3 install devsearch
```


## Configuration
`devsearch` is configured using an RC file.
The RC file specifies root directories in the file system that will be searched for projects.
The RC file specifies which version control systems will be considered valid.
git, svn, mercurial(hg), and cvs are supported.
```bash
me@tux:~/$ cat ~/.devsearchrc
[devsearch]
root = ~/projs:/classified/projects/:/tmp/garbage/projects
vcs = git:svn:hg:cvs
```

## Uninstallation
The following command will uninstall `devsearch`:
```bash
pip3 uninstall devsearch
```
