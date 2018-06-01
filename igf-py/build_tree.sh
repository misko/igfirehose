#!/bin/bash


if [ $# -ne 1 ]; then
	echo $0 root
	exit
fi

tag=$1

IGF=/ig/igfirehose/igf-py/

n=10000 #background sample
f_min=0.0001 # smallest fraction tag to consider
n_min=5000 # min for each hashtag before continuing 


mkdir -p /tmp/hashtag_${tag}
pushd /tmp/hashtag_${tag}
#1 get background keys
#1a get which keys occur for this root
n_mins="1000 5000 10000"
for n_min in ${n_mins}; do
	pushd ${IGF} 
	python ${IGF}/query_hashtags_raw.py -c ${IGF}/igf.conf -t $tag -n $n | python ${IGF}/analyze_hashtags.py - | awk -v f="$f_min" '{if ($1>f) {print $0}}' | while read line; do 
		this_tag=`echo $line | awk '{print $2}'`
		max_retries=15
		while [ `python ${IGF}/query_count.py -c ${IGF}/igf.conf -t ${this_tag}` -lt ${n_min} -a ${max_retries} -gt 0 -a `python ${IGF}/query_isdone.py -c ${IGF}/igf.conf -t ${this_tag}` = "None" ]; do
			scrapy crawl -a config_fn=${IGF}/igf.conf -a hashtag=${this_tag} -a n=${n_min} hashtag
			sleep 1
			echo MAX RETRY ${max_retries} ${this_tag}
			echo  `python ${IGF}/query_isdone.py -c ${IGF}/igf.conf -t ${this_tag}`
			max_retries=`expr ${max_retries} - 1`
		done
	done
	popd
done
