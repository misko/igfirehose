n=100

python query_hashtags_raw.py -t dogsofinstagram -c igf.conf -n $n | python analyze_hashtags.py - | awk '{print $2}' > dogsofinstagram.freq

cat  dogsofinstagram.freq | while read line; do 
	python query_co_p.py -c igf.conf -a dogsofinstagram -b $line > tmp.a &
	python query_isbreed.py -c igf.conf -t $line > tmp.b &
	python query_sim.py -c igf.conf -t dogsofinstagram,$line > tmp.c &
	python query_count.py -c igf.conf -t $line > tmp.d &
	wait
	echo "pr dogsofinstagram | $line " `cat tmp.a` `cat tmp.b` `cat tmp.c` `cat tmp.d`
	#echo "pr dogsofinstagram | $line " `python query_co_p.py -c igf.conf -a dogsofinstagram -b $line` `python query_isbreed.py -c igf.conf -t $line` `python query_sim.py -c igf.conf -t dogsofinstagram,$line`
done
