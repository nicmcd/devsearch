#!/bin/bash

if devsearch $@; then
    cd `cat ~/.devprj`
fi
