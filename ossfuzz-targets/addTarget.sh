#!/bin/bash

#set -xe
set -e

if [ $# -ne 1 ]
then
	echo "wrong usage, you should use it as: bash add_target.sh xxx"
	exit 1
fi

target=$1

if [ -d "$target" ]
then
	echo "$target already exists"
	exit 1
else
	cp -r template $target
	sed -i 's/TEMPLATE/'${target}'/g' ${target}/cfg.yml
	sed -i 's/template/'${target}'/g' ${target}/fuzzdrivergpt_build.sh
	echo "$target has been prepared"
fi