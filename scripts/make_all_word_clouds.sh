#!/bin/bash


p=/home/ubuntu/igfirehose/igfirehose
mkdir -p $p/igf-py/static/wordclouds/
python $p/igf-py/query_tags.py -c $p/igf-py/igf.conf | while read line; do 
	$p/scripts/make_wordcloud.sh $line $p
done
