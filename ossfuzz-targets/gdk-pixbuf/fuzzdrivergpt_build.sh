#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang

set -eux
# FILL HERE

set +eux

#
# do what should be done in build_fuzzers command
#
compile
#
#
#

##########
## After compile, you can prepare the include/lib staff here
##########

set -eux

##########
# UNCOMMENT this for manual exploration on how to write this fuzzdrivergpt_build.sh
# COMMENT this for testing the real logic of fuzzdrivergpt_build.sh
##########
#while true
#do
#	sleep 1h
#done


INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
mkdir -p ${INSTALL}/lib
mkdir -p ${INSTALL}/include

# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /work/prefix/include/gdk-pixbuf-2.0 ${INSTALL}/include/gdk-pixbuf-2.0

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp  /work/prefix/lib/libgdk_pixbuf-2.0.a ${INSTALL}/lib/libgdk_pixbuf-2.0.a
