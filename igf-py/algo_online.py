#from scipy.cluster.hierarchy import dendrogram, linkage
#from matplotlib import pyplot as plt
import csv
import argparse
import numpy as np
from IGFirehose import IGFirehose
import sys
from multiprocessing import Pool 
parser = argparse.ArgumentParser(
        prog='PROG',
        description='''Make linkage diagram? ''')
parser.add_argument("-s","--seed", help="seed",type=str,required=True)
parser.add_argument("-n","--number", help="hashtag",type=int, default=10000)
parser.add_argument("-hn","--hashtag-number", help="hashtag",type=int, default=10000)
parser.add_argument("-tn","--tag-number", help="hashtag",type=int, default=10000)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
parser.add_argument("-b", "--tag-back", help="tagback",type=float,default=0.005)
parser.add_argument("-o", "--online", help="tagback",type=int,default=20)
parser.add_argument("-t", "--threshold", help="t",type=int,default=0.0002)
args = parser.parse_args()


igf = IGFirehose(args.config)

#first get hashtags and lets check frequencies
def get_freq():
    h={}
    norm=0
    for img in igf.fetch(args.seed,n=args.hashtag_number,keys=('hashtags',)):
        if len(img['hashtags'])>0:
            norm+=1.0
            for x in img['hashtags']:
                if x not in h:
                    h[x]=0
                h[x]+=1
    for k in h:
        h[k]/=norm
    s=[ (h[k],k.encode('utf-8')[1:]) for k in h]
    s.sort(reverse=True)
    return s

def update_matrix(N):
    #make sure we have all needed entries
    for tagB in N:
	if tagB not in M:
		M[tagB]={}
		r=igf.get_co_p(N,tagB,n=args.number)
		#print "BIG CALL",tagB
		for idx in xrange(len(N)):
			M[tagB][N[idx]]=r[idx]
	else:
		for tagA in N:
			if tagA not in M[tagB]:
				# M[X][Y] = pr(X | Y )
				# co_p ( A , B ) = pr (A | B)
				#print "SMALL CALL",tagA,tagB
				M[tagB][tagA]=igf.get_co_p([tagA],tagB,n=args.number)[0]

def print_m(M,N):
    print ",".join( ["X"] + N)
    for i in N: # pick the row
        row=[]
        for j in N: # for each row
            if j==i:
                row.append(0)
		continue
	    row.append(M[i][j])
        print ",".join([i]+["%0.3e" % x for x in row]) 
	
# X is cotag matrix
# N is set of unused nodes
def prs(M,N):
    print_m(M,N)
    r={}
    for i in N: # pick the col
        r[i]=0
        norm=0
        for j in N: # for each row
            if j==i:
                continue
            r[i]+=M[j][i]
            norm+=1.0
        r[i]/=norm
    return r


freqs=get_freq()


p = Pool(16)
M={}
N=[args.seed] #,'poodle','goldenretriever']
S=[]
for _,tag in freqs:
	if tag==args.seed:
		continue
	#check the tag back
	tb=igf.get_co_p([args.seed],tag,n=args.tag_number)[0]
	if tb<args.tag_back:
		print "Dropping",tag,"because of tagback",tb,"<",args.tag_back
		continue
	N.append(tag)
	if len(N)>args.online: #try to reduce
		update_matrix(N)
		r=prs(M,N)
		vs=[ (float(r[i]),i) for i in r]
		vs.sort(reverse=True)
		argmax=vs[0]
		print "WINNER",argmax
		if argmax[0]>args.threshold:
			S.append(argmax[1])
			N.remove(argmax[1])
	




metric=[]
col_headers=[]
row_headers=[]
with open(args.csv, 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    col_headers = csvreader.next()[1:]
    for row in csvreader:
        metric.append(map(float,row[1:]))
        row_headers.append(row[0])

eq=True
for x in xrange(len(row_headers)):
    if row_headers[x]!=col_headers[x]:
        print "col and row headers need to be same :("
        sys.exit(1)

X=np.array(metric)


    
S,N=part(X,[],range(X.shape[0]))
print ",".join([ row_headers[x] for x in S]) 
print N
# X[i][j] = pr( tagged(j) | tagged(i) )


