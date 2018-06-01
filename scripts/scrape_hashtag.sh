#!/bin/bash

if [ $# -le 1 ]; then
	echo $0 hashtag [n]
	exit
fi

hashtag=$1
n=$2

pushd /tmp/igf

while [ 1 -lt 2 ]; do
         echo scrapy crawl -a config_fn=/tmp/igf/igf-py/igf.conf -a hashtag=$hashtag -a n=$n hashtag
         scrapy crawl -a config_fn=/tmp/igf/igf-py/igf.conf -a hashtag=$hashtag -a n=$n hashtag
         sleep 30
done
