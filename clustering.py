import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import pickle
import timeit
import math
import os

df = pd.read_csv('objects.data', sep=' ', names=['x','y'], index_col=False)
df.index = [i+1 for i in df.index]

class DistanceMatrix:

    def __init__(self, df, filename):
        self.filename=filename
        self.matrix = self.distanceArray(df)

    def distance(self, a, b):
        return math.sqrt(math.pow(a[0]-b[0], 2) + math.pow(a[1]-b[1], 2))

    def distanceArray(self, df, recalculate=False):
        if recalculate or not self.filename in os.listdir():
            tmp = np.zeros((df.shape[0], df.shape[0]))
            for i in range(df.shape[0]):
                for k in range(df.shape[0]):
                    if i<k:
                        tmp[i,k]=self.distance(tuple(df.iloc[i][['x','y']]),
                            tuple(df.iloc[k][['x','y']]))
            pickle.dump(tmp, open(self.filename, 'wb'))
            return tmp
        else:
            try:
                return pickle.load(open(self.filename, 'rb'))
            except:
                print('file does not exist')

    def getDist(self, el1, el2):
        return self.matrix[min(el1, el2),max(el1,el2)], el2

    def findNearestNode(self, array, searchspace):
        tmpdict={}
        for item in array:
            tmpdict[item]= min([self.getDist(item, e) for e in np.setdiff1d(
                searchspace,[item])])

        return min(tmpdict.items(), key=lambda x: x[1])

    def MST(self, nodes):
        tree=[]
        freeset=nodes
        size=0
        edges=[]

        if tree==[]:
            tree.append(freeset.pop())
        while freeset!=[]:
            intreepoint, (dist, newpoint) = self.findNearestNode(tree, freeset)
            tree.append(newpoint)
            freeset.remove(newpoint)
            edges.append((intreepoint, newpoint))
            size+=dist

        return size, edges

    def show(self, data, trees):
        for tree, i in zip(trees,range(len(trees))):
            for point in tree:
                plt.plot([data.iloc[point[0]].x, data.iloc[point[1]].x],
                        [data.iloc[point[0]].y, data.iloc[point[1]].y],
                        color=f'C{i}',linewidth=3)
        plt.scatter(data['x'], data['y'])
        plt.show()

    def greed(self, n):
        freeset=[i for i in range(len(self.matrix))]
        random.shuffle(freeset)
        clusters=[[freeset.pop()] for _ in range(n)]

        counter=0
        while freeset!=[]:
            _, (_,neighbor) = self.findNearestNode(clusters[counter%n], freeset)
            alt = []
            for cluster in clusters:
                t = [self.getDist(neighbor, node)[0] for node in cluster]
                alt.append(min(t))

            clusters[alt.index(min(alt))].append(neighbor)
            freeset.remove(neighbor)
            counter+=1
        return clusters

    def regret(self, n):
        freeset=[i for i in range(len(self.matrix))]
        random.shuffle(freeset)
        clusters=[[freeset.pop()] for _ in range(n)]

        counter=0
        while len(freeset)>1:
            _, (_,neighbor) = self.findNearestNode(clusters[counter%n], freeset)
            _, (_,alternative) = self.findNearestNode(clusters[counter%n],
                    np.setdiff1d(freeset,neighbor))
            others_a = []
            others_n = []
            for cluster in clusters:
                t = [self.getDist(neighbor, node)[0] for node in cluster+[alternative]]
                others_n.append(min(t))

                t = [self.getDist(alternative, node)[0] for node in cluster+[neighbor]]
                others_a.append(min(t))

            if min(others_n)<min(others_a):
                clusters[others_n.index(min(others_n))].append(neighbor)
                freeset.remove(neighbor)
            else:
                clusters[others_a.index(min(others_a))].append(alternative)
                freeset.remove(alternative)
            counter+=1

        _, (_,neighbor) = self.findNearestNode(clusters[counter%n], freeset)
        alt = []
        for cluster in clusters:
            t = [self.getDist(neighbor, node)[0] for node in cluster]
            alt.append(min(t))

        clusters[alt.index(min(alt))].append(neighbor)
        freeset.remove(neighbor)

        return clusters


    def greed2(self, n):
        freeset=[i for i in range(len(self.matrix))]
        random.shuffle(freeset)
        clusters=[[freeset.pop()] for _ in range(n)]

        while freeset!=[]:
            p = freeset.pop()
            tp = []
            for cluster in clusters:
                tmp=min([self.getDist(p, node)[0] for node in cluster])
                tp.append(tmp)
            clusters[tp.index(min(tp))].append(p)

        return clusters

    def regret2(self, n):
        freeset=[i for i in range(len(self.matrix))]
        random.shuffle(freeset)
        clusters=[[freeset.pop()] for _ in range(n)]

        while freeset!=[]:
            print()
            if len(freeset)>1:
                p1 = freeset.pop()
                p2 = freeset.pop()

                t =[]
                for cluster in clusters:
                    t.append(min([self.getDist(p2, node) for node in cluster]))
                p2t = t.index(min(t))
                tmpcluster = clusters[p2t]+[p2]

                t = []
                for cluster in clusters:
                    t.append(min([self.getDist(p1, node) for node in cluster]))
                p1t1 = t.index(min(t))

                t = []
                for cluster in clusters+[tmpcluster]:
                    t.append(min([self.getDist(p1, node) for node in cluster]))
                p1t2 = t.index(min(t))

                if p1t1==p1t2:
                    freeset.append(p2)
                    clusters[p1t1].append(p1)
                else:
                    freeset.append(p1)
                    clusters[p2t].append(p2)
            else:
                p1 = freeset.pop()
                t = []
                for cluster in clusters:
                    t.append(min([self.getDist(p1, node) for node in cluster]))
                p1t = t.index(min(t))
                clusters[p1t].append(p1)

        return clusters



dm=DistanceMatrix(df, 'matrix.p')

time=[]
scores=[]
trees=[]
last_best_score=999999
for _ in range(100):
    start = timeit.timeit()
    clusters = dm.greed2(10)
    end = timeit.timeit()
    time.append(end-start)

    outcome = [dm.MST(cluster) for cluster in clusters]
    score = sum([o[0] for o in outcome])
    scores.append(score)
    if score<last_best_score:
        last_best_score=score
        trees = [o[1] for o in outcome]

print('time avg: {}, min: {}, max: {}'.format(np.mean(time), min(time), max(time)))
print('score avg: {}, min: {}, max: {}'.format(np.mean(scores), min(scores), max(scores)))

dm.show(df, trees)
