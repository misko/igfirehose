from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt
import csv
import argparse
import numpy as np
from IGFirehose import IGFirehose
import sys
parser = argparse.ArgumentParser(
        prog='PROG',
        description='''Make linkage diagram? ''')
parser.add_argument("-s","--seed", help="seed",type=str,required=True)
parser.add_argument("-n","--number", help="hashtag",type=int, default=100)
parser.add_argument("-hn","--hashtag-number", help="hashtag",type=int, default=10000)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
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
    s=[ (h[k],k) for k in h]
    s.sort(reverse=True)
    return s

print get_freq()
sys.exit(1)





print igf.get_co_p([args.tagA],args.tagB,n=args.number)[0]



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



# X is cotag matrix
# N is set of unused nodes
def prs(X,N):
    r={}
    for i in N: # pick the col
        r[i]=0
        norm=0
        for j in N: # for each row
            if j==i:
                continue
            r[i]+=X[j][i]
            norm+=1.0
        r[i]/=norm
    return r

def part(X,S,N,t=0.002):
    r=prs(X,N)
    vs=[ (float(r[i]),i) for i in r]
    vs.sort(reverse=True)
    argmax=vs[0]
    if argmax[0]>t:
        S.append(argmax[1])
        N.remove(argmax[1])
        return part(X,S,N,t)
    return S,N
    
S,N=part(X,[],range(X.shape[0]))
print ",".join([ row_headers[x] for x in S]) 
print N
# X[i][j] = pr( tagged(j) | tagged(i) )


