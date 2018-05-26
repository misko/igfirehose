#!/bin/bash

mkdir -p /ig/igfirehose/igf-py/static/wordclouds/
python /ig/igfirehose/igf-py/query_tags.py -c /ig/igfirehose/igf-py/igf.conf | while read line; do 
	/ig/igfirehose/scripts/make_wordcloud.sh $line /ig/igfirehose/igf-py/static/wordclouds/${line}.png
done
