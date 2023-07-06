#!/bin/bash

set -e

if [ $# -ne 2 ]; then
	echo "Usage: $0 YOUR-OPENAI-APIKEY YOUR-OPENAI-ORGID"
	exit 1
fi

OPENAI_APIKEY=$1
OPENAI_ORGID=$2

# 1. install openai key and orgid into apikey.txt

if [ ! -f apikey.txt ]; then
	echo "OPENAI_APIKEY = ${OPENAI_APIKEY}" > apikey.txt
	echo "OPENAI_ORGID = ${OPENAI_ORGID}" >> apikey.txt

	echo "[+] apikey.txt installed"
else
	echo "[-] apikey.txt already exists, skip"
fi

# 2. install `jdk-19.0.2` into `./3rdparty/jdk-19.0.2`

if [ ! -d 3rdparty/jdk-19.0.2 ]; then
	wget https://download.java.net/java/GA/jdk19.0.2/fdb695a9d9064ad6b064dc6df578380c/7/GPL/openjdk-19.0.2_linux-x64_bin.tar.gz
	tar xf openjdk-19.0.2_linux-x64_bin.tar.gz
	mv jdk-19.0.2 3rdparty/

	# remove the download 
	rm openjdk-19.0.2_linux-x64_bin.tar.gz

	echo "[+] 3rdparty/jdk-19.0.2 installed"
else
	echo "[-] 3rdparty/jdk-19.0.2 already exists, skip"
fi

# 3. install python requirements

if [ ! -d venv ]; then
	mkdir venv

	virtualenv -p `which python3` venv

	. venv/bin/activate
	pip install -r requirements.txt
	deactivate

	echo "[+] venv installed"
else 
	echo "[-] venv already exists, skip"
fi

# 4. (Optional) install `src-cli` from [SourceGraph doc](https://github.com/sourcegraph/src-cli#installation-linux)

echo "[+] all done, you can now run the following commands to enter/leave the python env"
echo 
echo '>> Before running fuzzdrivergpt, enter the python env <<'
echo '  . venv/bin/activate'
echo 
echo '>> Leave the python env <<'
echo '  deactivate'
echo
