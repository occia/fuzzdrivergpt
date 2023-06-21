#!/bin/bash

absdir=$(dirname `realpath $0`)

echo "targets:"

bash ${absdir}/listTarget.sh | while read d
do
	sed 's/^/  /g' ${absdir}/${d}/cfg.yml
	echo
	echo
done
