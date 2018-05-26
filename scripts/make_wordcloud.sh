#!/bin/bash

if [ $# -ne 2 ]; then
	echo $0 tag output_file
	exit
fi

tag=$1
out=$2

python /ig/igfirehose/igf-py/query.py -c /ig/igfirehose/igf-py/igf.conf -t $tag -n 2000 | sed 's/^#//g' | wordcloud_cli.py --text - --background white --imagefile $out --no_collocations --height 300 --width 600
