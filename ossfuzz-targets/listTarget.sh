#!/bin/bash

absdir=$(dirname `realpath $0`)

for d in `ls ${absdir}`
do
	[ -d ${absdir}/$d ] && [[ ! -f ${absdir}/$d/SKIP ]] && echo $d
done 
