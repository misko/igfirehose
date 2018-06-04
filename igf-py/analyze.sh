n=300000

python query_hashtags_raw.py -t dogsofinstagram -c igf.conf -n $n | python analyze_hashtags.py - | awk '{print $2}' > dogsofinstagram.freq

cat  dogsofinstagram.freq | while read line; do 
	count=`python query_count.py -c igf.conf -t $line`
	if [ $count -gt 2000 ] ; then
	python query_co_p.py -c igf.conf -a dogsofinstagram -b $line -n 100000 > tmp.a &
	python query_isbreed.py -c igf.conf -t $line -n 100000 > tmp.b &
	python query_sim.py -c igf.conf -t dogsofinstagram,$line -n 100000 > tmp.c &
	wait
	echo "pr dogsofinstagram | $line " `cat tmp.a` `cat tmp.b` `cat tmp.c` $count
	#echo "pr dogsofinstagram | $line " `python query_co_p.py -c igf.conf -a dogsofinstagram -b $line` `python query_isbreed.py -c igf.conf -t $line` `python query_sim.py -c igf.conf -t dogsofinstagram,$line`
	fi
done
