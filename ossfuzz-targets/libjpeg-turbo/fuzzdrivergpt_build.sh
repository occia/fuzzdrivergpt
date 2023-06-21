#!/bin/bash

##########
# UNCOMMENT this for manual exploration on how to write this fuzzdrivergpt_build.sh
# COMMENT this for testing the real logic of fuzzdrivergpt_build.sh
##########
#while true
#do
#	sleep 1h
#done

##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang

set -eux
cat >> /src/libjpeg-turbo.main/fuzz/build.sh << 'EOF'
cmake . -DCMAKE_BUILD_TYPE=RelWithDebInfo -DENABLE_STATIC=1 -DENABLE_SHARED=0 \
        -DCMAKE_C_FLAGS_RELWITHDEBINFO="-g -DNDEBUG" \
        -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-g -DNDEBUG" -DCMAKE_INSTALL_PREFIX=/src/libjpeg-turbo.main/fuzzdrivergpt-install \
        -DWITH_FUZZ=1 -DFUZZ_BINDIR=$OUT -DFUZZ_LIBRARY=$LIB_FUZZING_ENGINE \
        -DFUZZER_SUFFIX="$FUZZER_SUFFIX"
make clean
make "-j$(nproc)" "--load-average=$(nproc)"
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

INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/libjpeg-turbo.main/fuzzdrivergpt-install/include /root/workspace/fuzzdrivergpt/install/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/libjpeg-turbo.main/fuzzdrivergpt-install/lib /root/workspace/fuzzdrivergpt/install/lib
