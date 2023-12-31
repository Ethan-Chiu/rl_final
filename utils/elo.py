from collections import OrderedDict
import matplotlib.pyplot as plt
import random

iterations = 100
games = 500
names = ["Original AlphaZero", "Our method"]
bases = 4
visualize = True

mult = 0
winrate = []
for n in range(len(names)):
    win = [0] * (bases+1)
    print(names[n] + ':')
    for i in range(bases+1):
        win[i] = input()
    winrate.append([[float(k) for k in z.split()] for z in win])
    mult += (len(winrate[-1])-1) * len(winrate[-1][0])
games *= mult

class Elo:
    def __init__(self, k):
        self.ratings = OrderedDict([])	
        self.k = k

    def addPlayer(self, name, rating=1000):
        self.ratings[name] = rating

    def game(self, a, b, r):
        result = 1/((10.0**(min((self.ratings[b]-self.ratings[a])/400.0, 255)))+1)
        # if a[:2] == 'az':
            # self.ratings[a] = max(self.ratings[a] + self.k * (r - result), 0)
        # if b[:2] == 'az':
            # self.ratings[b] = max(self.ratings[b] + self.k * (result - r), 0)
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


avg = OrderedDict([])	
players = [names[n] + '@'+str(int(z)) for n in range(len(names)) for z in winrate[n][0]]
baselines = ['mcts10', 'mcts100', 'mcts1000', 'mcts10000'][:bases]
for t in range(iterations):
    elo = Elo(k = 10)
    for z in baselines:
        elo.addPlayer(z)
    for z in players:
        elo.addPlayer(z)
    for z in range(games):
        q = random.random()
        if q < 0.1:
            i = random.randrange(len(baselines))
            j = random.randrange(len(baselines))
            if i < j:
                elo.game(baselines[i], baselines[j], 0)
        elif q > 0.9:
            i = random.randrange(1, len(winrate[0][0]))
            elo.game(names[0]+'@'+str(int(winrate[0][0][i])), names[1]+'@'+str(int(winrate[1][0][i])), 0)
        else:
            a = random.randrange(0, len(winrate))
            b = random.randrange(0, len(winrate[a][0])) 
            c = random.randrange(0, bases)
            d = 1 if random.random() < winrate[a][c+1][b]/2 else 0
            elo.game(names[a]+'@'+str(int(winrate[a][0][b])), baselines[c], d)
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
    baselines = {}
    maxstep = 0
    for k in avg.keys():
        if len(k) > 4 and k[:4] == "mcts":
            baselines[int(k[4:])] = avg[k]
            continue
        name, step = k.split('@')
        step = int(step)
        if name not in chart:
            chart[name] = [[step], []]
        else:
            chart[name][0].append(step)
        chart[name][1].append(avg[k])
        maxstep = max(step, maxstep)
    for n in chart:
        x, y = zip(*sorted(zip(chart[n][0], chart[n][1])))
        plt.plot(x, y, label=n, marker='.')
    for b in baselines:
        plt.axhline(y=baselines[b], color='k', linestyle='--')
        plt.text(60, baselines[b] -10, 'mcts'+str(b), color='k', verticalalignment='top', horizontalalignment='right')
    plt.legend()
    plt.xlabel('time', fontsize="10")
    plt.ylabel('elo', fontsize="10")
    plt.show()
