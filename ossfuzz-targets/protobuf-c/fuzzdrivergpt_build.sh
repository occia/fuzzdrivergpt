#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang
export MAKEFLAGS="-j`nproc`"
#sed -i 's#configure#configure --prefix=/src/protobuf-c/fuzzdrivergpt-install#g' /src/build.sh
set -eux
# FILL HERE
cat >> /src/build.sh << 'EOF'
cd /src/protobuf-c
./configure --enable-static=yes --enable-shared=false --prefix=/src/protobuf-c/fuzzdrivergpt-install
make -j$(nproc)
make install

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
cp -r /src/protobuf-c/fuzzdrivergpt-install/include ${INSTALL}/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/protobuf-c/fuzzdrivergpt-install/lib ${INSTALL}/lib
