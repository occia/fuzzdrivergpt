#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang
export MAKEFLAGS="-j`nproc`"
echo set\(CMAKE_VERBOSE_MAKEFILE ON\) >> /src/utf8proc/CMakeLists.txt
set -eux
# FILL HERE
cat >> /src/utf8proc/test/ossfuzz.sh << 'EOF'
cd /src/utf8proc
cd build
cmake .. -DUTF8PROC_ENABLE_TESTING=ON -DLIB_FUZZING_ENGINE="$LIB_FUZZING_ENGINE" --install-prefix=/src/utf8proc/fuzzdrivergpt-install
V=1 make  -j$(nproc) install

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


INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/utf8proc/fuzzdrivergpt-install/include ${INSTALL}/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/utf8proc/fuzzdrivergpt-install/lib ${INSTALL}/lib
