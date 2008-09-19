"""
Synthetic Test for hcluster - generates a small number of cluster centres, and places 
points randomly around them.  In 2D space, so easy to visualise.
"""
import hcluster
from numpy import *
from pylab import *

rseed=1
seed(rseed)  # 0 is a case with two centres very close - 1 is better
ntot=40
ncl=6
x=zeros(ntot) ; y=x.copy()
xc=random(ncl)
yc=random(ncl)
spread=0.1   # 0.2 is like our data  0.1 is cleaner

for i in arange(0,ntot):
    j=random_integers(ncl)-1
    x[i]=xc[j] + (random()-0.5)*spread
    y[i]=yc[j] + (random()-0.5)*spread

distances=[]
indices=[]
# this loop needs to be re-written!
for (i,xx) in enumerate(x[:-1]):
    for (j,xxx) in enumerate(x[i+1:]):
        distances.append(sqrt((x[i]-x[j+i+1])**2 + (y[i]-y[j+i+1])**2))
        indices.append([i,j+i+1])
figure()
plot(xc,yc,'o')
plot(x,y,'.')
titl=str("%d points, %d clusters, %g spread, seed = %d" % (ntot, ncl, spread, rseed))
title(titl)
show()
figure()
Y = hcluster.linkage(distances)
X = hcluster.dendrogram(Y)
title(titl)
show()
