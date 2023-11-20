from collections import OrderedDict
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
        self.sort()

    def sort(self):
        self.ratings = OrderedDict([(k,v) for k, v in sorted(self.ratings.items(), key=lambda i: i[1])])

    def select(self):
        a = random.choice(list(self.ratings.keys()))
        b = random.choice(list(self.ratings.keys()))
        while b == a:
            b = random.choice(list(self.ratings.keys()))
        return a, b

import mcts
from mcts import FLAGS
from absl import app
import random
num_matches = 0
FLAGS.num_games = 10
agents = {"mcts2": ["mcts", 2], "random": ["random", 0], "mcts10": ["mcts", 10], "mcts100": ["mcts", 100], "mcts1000": ["mcts", 1000]}
names = "mcts2 random mcts10 mcts100 mcts1000".split()
elo = Elo(k = 10)
for a in agents.keys():
    elo.addPlayer(a)
for m in range(num_matches):
    for i in range(5):
        for j in range(5):
            if i == j:
                continue
            a = names[i]
            b = names[j]
            FLAGS.player1 = agents[a][0]
            FLAGS.max_simulations = agents[a][1]
            FLAGS.player2 = agents[b][0]
            FLAGS.max_simulations2 = agents[b][1]
            try:
                app.run(mcts.main)
            except:
                pass

elo.addPlayer("az")
for m in range(num_matches):
    for i in range(5):
        a = names[i]
        FLAGS.player1 = agents[a][0]
        FLAGS.max_simulations = agents[a][1]
        FLAGS.player2 = "az"
        try:
            app.run(mcts.main)
        except:
            pass
        FLAGS.player2 = agents[a][0]
        FLAGS.max_simulations2 = agents[a][1]
        FLAGS.player1 = "az"
        try:
            app.run(mcts.main)
        except:
            pass

f = open('arena.log', 'r')
lines = f.readlines()
for z in range(5):
    for line in lines:
        g = line.split('/')
        results = eval(g[2])
        for i in results:
            elo.game(g[0], g[1], (i+1)/2)
print(elo.ratings)
