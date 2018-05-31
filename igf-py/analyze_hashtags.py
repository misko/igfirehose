import sys

if len(sys.argv)!=2:
    print "%s in_file"
    sys.exit(1)

in_file=sys.argv[1]

hashtag_counts_d={}
posts_with_hashtags=0
f=sys.stdin
if in_file!='-':
    f=open(in_file)
for line in f:
    if len(line.strip())>0:
        posts_with_hashtags+=1
    line=line.strip().split()
    for hashtag in line:
        if len(hashtag)>0:
            if hashtag not in hashtag_counts_d:
                hashtag_counts_d[hashtag]=0
            hashtag_counts_d[hashtag]+=1

hashtag_counts=[]
for hashtag in hashtag_counts_d:
    hashtag_counts.append((hashtag_counts_d[hashtag],hashtag))

hashtag_counts.sort(reverse=True)

for count,hashtag in hashtag_counts:
    if count>4:
        print float(count)/posts_with_hashtags,hashtag

#get top 100 tags and graph
#get top 101-200 tags and graph

#determine co-orccurence of tags (minus most popular - one that was mined) > X threshold and print 
