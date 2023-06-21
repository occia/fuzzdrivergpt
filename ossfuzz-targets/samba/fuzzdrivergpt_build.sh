#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang
export MAKEFLAGS="-j`nproc`"
set -eux
#sed -i 's#./configure#./configure --prefix=/src/samba/fuzzdrivergpt-install#g' /src/samba/lib/fuzzing/oss-fuzz/do_build.sh
# FILL HERE
#/src/samba/lib/fuzzing/oss-fuzz/build_image.sh

cat >> /src/samba/lib/fuzzing/oss-fuzz/do_build.sh << 'EOF'
cd /src/samba
make -j$(nproc) install
rm -rf /src/samba/bin
rm -rf /out/*
EOF
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


