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
parser.add_argument("-sb","--seed-breed", help="seed-breed",type=str,required=False,default="")
parser.add_argument("-sd","--seed-synonym", help="seed-synonym",type=str,required=False,default="")
parser.add_argument("-n","--number", help="hashtag",type=int, default=10000)
parser.add_argument("-hn","--hashtag-number", help="hashtag",type=int, default=10000)
parser.add_argument("-tn","--tag-back-number", help="hashtag",type=int, default=10000)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
parser.add_argument("-b", "--tag-back", help="tagback",type=float,default=0.005)
parser.add_argument("-o", "--online", help="tagback",type=int,default=20)
parser.add_argument("-t", "--threshold", help="t",type=int,default=0.0002)
parser.add_argument("-p", "--pool-size", help="pool size",type=int,default=16)
parser.add_argument("-d", "--out-dir", help="out-dir",type=str,default='algo_out')
parser.add_argument("-g", "--sigma", help="out-dir",type=float,default=3.0)
args = parser.parse_args()
import errno    
import os

#https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

mkdir_p(args.out_dir)
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



def update_helper(a):
    tagAs,tagB=a
    igf = IGFirehose(args.config)
    return igf.get_co_p(tagAs,tagB,n=args.number)
    

def update_matrix(N):
    #make sure we have all needed entries
    todo=[]
    for tagB in N:
	if tagB not in M:
		todo.append((N,tagB))
		#M[tagB]={}
		#r=igf.get_co_p(N,tagB,n=args.number)
		#for idx in xrange(len(N)):
		#	M[tagB][N[idx]]=r[idx]
	else:
		for tagA in N:
			if tagA not in M[tagB]:
				todo.append(([tagA],tagB))
				#M[tagB][tagA]=igf.get_co_p([tagA],tagB,n=args.number)[0]
    rmap=p.map(update_helper, todo)
    for i in xrange(len(todo)):
        tagAs,tagB = todo[i] #input
        r=rmap[i] #output
        if tagB not in M:
            M[tagB]={}
        for j in xrange(len(tagAs)):
    	    M[tagB][tagAs[j]]=r[j]
	

def print_m(M,N,col_stats=None):
    s=[",".join( ["X"] + N)]
    for i in N: # pick the row
        row=[]
        for j in N: # for each row
            if j==i:
                row.append(0)
		continue
            if col_stats!=None:
	        row.append(np.abs(M[i][j]-col_stats[j]['avg'])/(col_stats[j]['std']+0.0001))
            else:
	        row.append(M[i][j])
        s.append(",".join([i]+["%0.3e" % x for x in row]) )	
    return "\n".join(s) 


def remove_outliers(acc):
	acc=np.array(acc)
	std=acc.std()
	avg=acc.mean()
	acc_no_outliers=[]
	for x in acc:
		if np.abs((x-avg)/std)>args.sigma:
			pass
		else:
			acc_no_outliers.append(x)
	return len(acc_no_outliers)==len(acc),acc_no_outliers,avg,std
		
# X is cotag matrix
# N is set of unused nodes
def prs(M,N):
    r={}
    col_stats={}
    for i in N: # pick the col
        acc=[]
        for j in N: # for each row
            if j==i: # or M[j][i]<0.000000001:
                continue
            acc.append(M[j][i])
        #outlier removal
        stop=False
        acc_no_outliers=np.array(acc)
        while not stop:
            stop,acc_no_outliers,avg,std=remove_outliers(acc_no_outliers)
            col_stats[i]={'avg':avg,'std':std}
            if len(acc_no_outliers)<(len(acc)/2):
                stop=True
        r[i]=sum(acc_no_outliers)/len(acc_no_outliers)
        if len(acc_no_outliers)!=len(acc):
            print "REMOVED",len(acc)-len(acc_no_outliers),"Outliers from",i
        else:
            print "NOTHING REMOVED?",i
    return r,col_stats

p = Pool(args.pool_size)

freqs=get_freq()


M={}
B=[]
N=[args.seed] #,'poodle','goldenretriever']
S=[]
if args.seed_breed!="":
	f=open(args.seed_breed)
	for line in f:
		line=line.strip()
		B.append(line)
		N.append(line)
	f.close()
if args.seed_synonym!="":
	f=open(args.seed_synonym)
	for line in f:
		line=line.strip()
		S.append(line)
for _,tag in freqs:
	if tag==args.seed:
		continue
	if tag in S:
		continue
	if tag in N:
		continue
	#check the tag back
	tb=igf.get_co_p([args.seed],tag,n=args.tag_back_number)[0]
	if tb<args.tag_back:
		print "Dropping",tag,"because of tagback",tb,"<",args.tag_back
		continue
	N.append(tag)
	if len(N)>args.online: #try to reduce
		update_matrix(N)
		r,col_stats=prs(M,N)
		vs=[ (float(r[i]),i) for i in r]
		vs.sort(reverse=True)

		#idx
		idx=0
		while idx<len(vs):
			argmax=vs[idx]
			if argmax[1] not in B:
				break
			idx+=1
		if idx==len(vs):
			continue	
		print "WINNER",argmax
		if argmax[0]>args.threshold:
			matrix=print_m(M,N)
			matrix_zo=print_m(M,N,col_stats=col_stats)
			f=open(args.out_dir+'/'+argmax[1]+'.txt','w')
			f.write(str(argmax)+'\n')
			f.write(str(r)+'\n')
			f.write(",".join(N)+'\n')
			f.write(",".join(S)+'\n')
			f.write(matrix+'\n')
			f.write('\n')
			f.write('\n')
			f.write(matrix_zo+'\n')
			f.close()
			S.append(argmax[1])
			N.remove(argmax[1])
	




f=open('N.txt','w')
f.write([ "\n".join([ str(x) for x in N ])])
f=open('S.txt','w')
f.write([ "\n".join([ str(x) for x in S ])])
