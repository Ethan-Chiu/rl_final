from collections import OrderedDict
import random

log = 'battle.log'
mcts = [2, 5, 10, 30]
az = [i for i in range(0,570,30)]
iterations = 100

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


f = open(log, 'r')
lines = f.readlines()
avg = OrderedDict([])	
for m in mcts:
    avg["mcts"+str(m)] = 0
for a in az:
    avg["az"+str(a)] = 0
for t in range(iterations):
    random.shuffle(lines)
    elo = Elo(k = 10)
    for m in mcts:
        elo.addPlayer("mcts"+str(m))
    for a in az:
        elo.addPlayer("az"+str(a))
    for l in lines:
        g = l.split('/')
        results = eval(g[2])
        for i in results:
            elo.game(g[0], g[1], (i+1)/2)
        g = l.split('/')
        results = eval(g[2])
        for i in results:
            elo.game(g[0], g[1], (i+1)/2)
    for a in elo.ratings:
        avg[a] += elo.ratings[a]
avg = OrderedDict([(k,v) for k, v in sorted(avg.items(), key=lambda i: i[1])])
for l in reversed(list(avg)):
    print(l, avg[l]/iterations)
