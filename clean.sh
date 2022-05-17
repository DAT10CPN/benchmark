#!/bin/bash

# Args: [dir]

DIR=$1

if [ -z "$DIR" ] ; then
  DIR="output"
  rm slurm*
fi

rm -r "DIR"

