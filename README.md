# devsearch

This project implements a simple system for finding the project I want to work on and changing my current directory to it.

    Me@tux:~/$ dev linux
      loading '~/dev/github/torvalds/linux'

    me@tux:~/dev/github/torvalds/linux$

If there is more than one match, an option list will be presented:

    me@tux:~/$ dev linux
      project [1] '~/dev/github/torvalds/linux'
      project [2] '~/dev/github/raspberrypi/linux'
      project [3] '~/dev/github/svenkatr/linux'
      choose a project: 2

    me@tux:~/dev/github/raspberrypi/linux$
