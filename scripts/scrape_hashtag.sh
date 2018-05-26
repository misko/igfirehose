#!/bin/bash

if [ $# -ne 1 ]; then
	echo $0 hashtag
	exit
fi

hashtag=$1

pushd /tmp/igf

while [ 1 -lt 2 ]; do
         scrapy crawl -a config_fn=/tmp/igf/igf-py/igf.conf $1
         sleep 30
done
