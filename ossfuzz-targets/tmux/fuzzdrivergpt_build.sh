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
cd /src/tmux
./configure --prefix=/src/tmux/fuzzdrivergpt-install \
    --enable-fuzzing \
    FUZZING_LIBS="${LIB_FUZZING_ENGINE} -lc++" \
    LIBEVENT_LIBS="-Wl,-Bstatic -levent -Wl,-Bdynamic" \
    LIBTINFO_LIBS=" -l:libtinfo.a "
make -j$(nproc) install
ar rcs libtmux.a compat/closefrom.o compat/fgetln.o compat/freezero.o compat/getdtablecount.o compat/getpeereid.o compat/getprogname.o compat/setproctitle.o compat/strlcat.o compat/strlcpy.o compat/strtonum.o compat/reallocarray.o compat/recallocarray.o compat/getopt.o compat/imsg.o compat/imsg-buffer.o compat/vis.o compat/unvis.o compat/fdforkpty.o alerts.o arguments.o attributes.o cfg.o client.o cmd-attach-session.o cmd-bind-key.o cmd-break-pane.o cmd-capture-pane.o cmd-choose-tree.o cmd-command-prompt.o cmd-confirm-before.o cmd-copy-mode.o cmd-detach-client.o cmd-display-menu.o cmd-display-message.o cmd-display-panes.o cmd-find-window.o cmd-find.o cmd-if-shell.o cmd-join-pane.o cmd-kill-pane.o cmd-kill-server.o cmd-kill-session.o cmd-kill-window.o cmd-list-buffers.o cmd-list-clients.o cmd-list-keys.o cmd-list-panes.o cmd-list-sessions.o cmd-list-windows.o cmd-load-buffer.o cmd-lock-server.o cmd-move-window.o cmd-new-session.o cmd-new-window.o cmd-parse.o cmd-paste-buffer.o cmd-pipe-pane.o cmd-queue.o cmd-refresh-client.o cmd-rename-session.o cmd-rename-window.o cmd-resize-pane.o cmd-resize-window.o cmd-respawn-pane.o cmd-respawn-window.o cmd-rotate-window.o cmd-run-shell.o cmd-save-buffer.o cmd-select-layout.o cmd-select-pane.o cmd-select-window.o cmd-send-keys.o cmd-server-access.o cmd-set-buffer.o cmd-set-environment.o cmd-set-option.o cmd-show-environment.o cmd-show-messages.o cmd-show-options.o cmd-show-prompt-history.o cmd-source-file.o cmd-split-window.o cmd-swap-pane.o cmd-swap-window.o cmd-switch-client.o cmd-unbind-key.o cmd-wait-for.o cmd.o colour.o control-notify.o control.o environ.o file.o format.o format-draw.o grid-reader.o grid-view.o grid.o hyperlinks.o input-keys.o input.o job.o key-bindings.o key-string.o layout-custom.o layout-set.o layout.o log.o menu.o mode-tree.o names.o notify.o options-table.o options.o paste.o popup.o proc.o regsub.o resize.o screen-redraw.o screen-write.o screen.o server-acl.o server-client.o server-fn.o server.o session.o spawn.o status.o style.o tmux.o tty-acs.o tty-features.o tty-keys.o tty-term.o tty.o utf8.o window-buffer.o window-client.o window-clock.o window-copy.o window-customize.o window-tree.o window.o xmalloc.o osdep-linux.o

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


#INSTALL=/root/workspace/fuzzdrivergpt/install
#mkdir -p ${INSTALL}
## copy the headers to /root/workspace/fuzzdrivergpt/install/include
#cp -r /src/tmux/fuzzdrivergpt-install/include ${INSTALL}/include
#
## copy the libs to /root/workspace/fuzzdrivergpt/install/lib
#cp -r /src/tmux/fuzzdrivergpt-install/lib ${INSTALL}/lib
