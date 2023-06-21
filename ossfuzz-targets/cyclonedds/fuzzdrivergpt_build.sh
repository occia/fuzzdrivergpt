#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang

set -eux
# FILL HERE
cat >> /src/build.sh << 'EOF'

cd /src/cyclonedds/build
rm -rf ./*
cmake -DBUILD_IDLC=ON  -DBUILD_TESTING=ON  -DBUILD_SHARED_LIBS=OFF -DBUILD_EXAMPLES=NO  -DENABLE_SECURITY=NO   -DENABLE_SSL=NO  -DCMAKE_INSTALL_PREFIX=/src/cyclonedds/fuzzdrivergpt-install  ..
cmake --build .
cmake --build . --target install
cd ..
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
cp -r /src/cyclonedds/fuzzdrivergpt-install/include ${INSTALL}/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/cyclonedds/fuzzdrivergpt-install/lib ${INSTALL}/lib
