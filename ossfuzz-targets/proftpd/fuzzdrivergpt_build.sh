#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang
export MAKEFLAGS="-j`nproc`"
set -eux
# FILL HERE
cat >> /src/proftpd/tests/fuzzing/oss_fuzz_build.sh << 'EOF'

pushd /src/proftpd
./configure --enable-ctrls --prefix=/src/proftpd/fuzzdrivergpt-install
make -j$(nproc) install
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
#

INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
mkdir -p ${INSTALL}/lib
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/proftpd/fuzzdrivergpt-install/include ${INSTALL}/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp /src/proftpd/lib/prbase.a  ${INSTALL}/lib/prbase.a
cp /src/proftpd/fuzz_lib.a  ${INSTALL}/lib/fuzz_lib.a
cp -r /src/proftpd/fuzzdrivergpt-install/lib ${INSTALL}/lib
