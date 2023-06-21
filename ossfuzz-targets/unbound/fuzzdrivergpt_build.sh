#!/bin/bash



##########
## Before compile, you can modify build.sh for eaiser preparation here
##########
# install libclang for our python usage, do this for all oss-fuzz projects
apt install -y clang
pip3 install libclang
ln -s /usr/lib/llvm-10/lib/libclang.so.1 /usr/local/lib/python3.8/site-packages/clang/native/libclang.so
export MAKEFLAGS="-j`nproc`"
set -eux
# FILL HERE
cat >> /src/build.sh << 'EOF'
cd /src/unbound
#ar rcs libunbound.a dns.o infra.o rrset.o dname.o msgencode.o as112.o msgparse.o msgreply.o packed_rrset.o iterator.o iter_delegpt.o iter_donotq.o iter_fwd.o iter_hints.o iter_priv.o iter_resptype.o iter_scrub.o iter_utils.o localzone.o mesh.o modstack.o view.o outbound_list.o alloc.o config_file.o configlexer.o configparser.o fptr_wlist.o edns.o locks.o log.o mini_event.o module.o net_help.o random.o rbtree.o regional.o rtt.o dnstree.o lookup3.o lruhash.o slabhash.o tcp_conn_limit.o timehist.o tube.o winsock_event.o autotrust.o val_anchor.o validator.o val_kcache.o val_kentry.o val_neg.o val_nsec3.o val_nsec.o val_secalgo.o val_sigcrypt.o val_utils.o dns64.o authzone.o respip.o netevent.o listen_dnsport.o outside_network.o ub_event.o keyraw.o sbuffer.o wire2str.o parse.o parseutil.o rrdef.o str2wire.o libunbound.o libworker.o context.o rpz.o proxy_protocol.o strlcat.o strlcpy.o arc4random.o arc4random_uniform.o arc4_lock.o

./configure --prefix=/src/unbound/fuzzdrivergpt-install
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


INSTALL=/root/workspace/fuzzdrivergpt/install
mkdir -p ${INSTALL}
# copy the headers to /root/workspace/fuzzdrivergpt/install/include
cp -r /src/unbound/fuzzdrivergpt-install/include ${INSTALL}/include

# copy the libs to /root/workspace/fuzzdrivergpt/install/lib
cp -r /src/unbound/fuzzdrivergpt-install/lib ${INSTALL}/lib
