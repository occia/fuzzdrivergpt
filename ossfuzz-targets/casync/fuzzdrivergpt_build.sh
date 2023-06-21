#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang
export MAKEFLAGS="-j`nproc`"
set -eux
# FILL HERE
cat >> /src/casync/tools/oss-fuzz.sh << 'EOF'
set -x
#cd /src/casync
#meson $build -D$fuzzflag \
#      -Db_lundef=false \
#      -Dlibzstd=disabled \
#      -Dman=false --prefix=/src/casync/fuzzdrivergpt-install
#ninja --verbose -C $build fuzzers
#ninja -C $build install


EOF
set +eux
#while true
#do
#	sleep 1h
#done
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



#INSTALL=/root/workspace/fuzzdrivergpt/install
#mkdir -p ${INSTALL}
## copy the headers to /root/workspace/fuzzdrivergpt/install/include
#cp -r /src/casync/fuzzdrivergpt-install/include ${INSTALL}/include
#
## copy the libs to /root/workspace/fuzzdrivergpt/install/lib
#cp -r /src/casync/fuzzdrivergpt-install/lib ${INSTALL}/lib
