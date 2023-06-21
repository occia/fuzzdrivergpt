#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang
export MAKEFLAGS="-j`nproc`"
set -eux
# FILL HERE
cat >> /src/build.sh << 'EOF'

mkdir /src/htslib1
cd /src/htslib1
git clone https://github.com/samtools/htslib.git
cd htslib 
git submodule update --init --recursive
make clean
autoreconf -i  # Build the configure script and install files it uses
./configure --prefix=/src/htslib/fuzzdrivergpt-install
make install -j$(nproc)


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
cd /src/htslib1/htslib
make clean
autoreconf -i  # Build the configure script and install files it uses
./configure --prefix=/src/htslib/fuzzdrivergpt-install
make install -j$(nproc)


INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/htslib/fuzzdrivergpt-install/include ${INSTALL}/include

#copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/htslib/fuzzdrivergpt-install/lib ${INSTALL}/lib

# while true
# do
# 	sleep 1h
# done
