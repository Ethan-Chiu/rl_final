from collections import OrderedDict
import matplotlib.pyplot as plt
import random

logs = ['battle18.log', 'battle19.log', 'battle20.log']
iterations = 100
visualize = True

class Elo:
    def __init__(self, k):
        self.ratings = OrderedDict([])	
        self.k = k

    def addPlayer(self, name, rating=1000):
        self.ratings[name] = rating

    def game(self, a, b, r):
        result = 1/((10.0**(min((self.ratings[b]-self.ratings[a])/400.0, 255)))+1)
        self.ratings[a] = max(self.ratings[a] + self.k * (r - result), 0)
        self.ratings[b] = max(self.ratings[b] + self.k * (result - r), 0)
        # self.sort()

    def sort(self):
        self.ratings = OrderedDict([(k,v) for k, v in sorted(self.ratings.items(), key=lambda i: i[1])])

    def select(self):
        a = random.choice(list(self.ratings.keys()))
        b = random.choice(list(self.ratings.keys()))
        while b == a:
            b = random.choice(list(self.ratings.keys()))
        return a, b


lines = []
for log in logs:
    f = open(log, 'r')
    lines.extend(f.readlines())
avg = OrderedDict([])	
for t in range(iterations):
    random.shuffle(lines)
    elo = Elo(k = 10)
    for l in lines:
        g = l.split('/')
        for gi in g[:2]:
            if gi not in elo.ratings:
                elo.addPlayer(gi)
        results = eval(g[2])
        for i in results:
            elo.game(g[0], g[1], (i+1)/2)
    for a in elo.ratings:
        if a not in avg:
            avg[a] = elo.ratings[a]/iterations
        else:
            avg[a] += elo.ratings[a]/iterations
avg = OrderedDict([(k,v) for k, v in sorted(avg.items(), key=lambda i: i[1])])
for l in reversed(list(avg)):
    print(l, avg[l])

if visualize:
    chart = {}
    for k in avg.keys():
        found = False
        algindex = -1
        for index, char in enumerate(k):
            if char.isdigit():
                if algindex == -1:
                    algindex = index
                found = True
            elif found and not char.isdigit():
                step = int(k[algindex:index])
                alg = k[:algindex]
                name = k[index:]
                break
        if name not in chart:
            chart[name] = [[step], [avg[k]]]
        else:
            chart[name][0].append(step)
            chart[name][1].append(avg[k])
    for n in chart:
        x, y = zip(*sorted(zip(chart[n][0], chart[n][1])))
        plt.plot(x, y)
    plt.show()
