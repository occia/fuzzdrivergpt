#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
pip3 install libclang
sed -i 's#make#make -j$(nproc)#g' /src/build.sh
set -eux
# FILL HERE
cat >> /src/build.sh << 'EOF'

make clean
./configure CC="$CC" CFLAGS="$CFLAGS" LDFLAGS="$CFLAGS" --disable-shared --disable-hardening --enable-pie --prefix=/src/lldpd/fuzzdrivergpt-install
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
###########
#while true
#do
#	sleep 1h
#done


INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
mkdir -p ${INSTALL}/include/daemon
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/lldpd/fuzzdrivergpt-install/include/* ${INSTALL}/include
cp -r /src/lldpd/src/daemon/*.h  ${INSTALL}/include/daemon

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/lldpd/fuzzdrivergpt-install/lib ${INSTALL}/lib
