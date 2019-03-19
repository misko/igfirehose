#!/bin/bash

if [ $# -ne 2 ]; then
	echo $0 tag root
	exit
fi

tag=$1
root=$2

python $root/igf-py/query_hashtags.py -c $root/igf-py/igf.conf -t $tag -n 2000 | sed 's/^#//g' | wordcloud_cli --text - --background white --imagefile $root/igf-py/static/wordclouds/${line}.png --no_collocations --height 300 --width 600
