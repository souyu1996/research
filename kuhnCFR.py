from random import shuffle
import random

class KuhnPoker:
    def __init__(self):
        self.cards=[1,2,3]
        self.init_game()

    def init_game(self):
        random.shuffle(self.cards)
        self.history=""

    def reshuffle(self):
        self.init_game()

    def is_end(self,play_list):
        history=self.history
        lenh = len(history)
        [player,opponent]=play_list
        if lenh > 1:
            terminalPass = history[-1] == "p"
            doubleBet = history[lenh - 2:] == "bb"
            isPlayerCardHigher = self.cards[player] > self.cards[opponent]
            if terminalPass:
                if history == "pp":
                    if isPlayerCardHigher:
                        return  1
                    else:
                        return -1
                else:
                    return 1
            elif doubleBet:
                if isPlayerCardHigher:
                    return 2
                else:
                    return -2
        return 0

    def run(self,players):
        play_list=list(range(len(players)))
        random.shuffle(play_list)
        while 1:    #此处可改成step函数
            player=play_list[0]
            rew=self.is_end(self.history,play_list)
            if rew!=0:
                return player,rew
            a=players[player].get_action(self.history,self.cards)
            #update history
            self.update(a)
            #update player
            play_list=play_list[::-1]   #改用queue管理

    def update(self,action):
        self.history+=str(action)

    def withdraw(self):
        self.history=self.history[:-1]

class Player:
    def __init__(self,name=None):
        self.PASS = 0
        self.BET = 1
        self.NUM_ACTIONS = 2
        self.ACTIONS=["p","b"]
        self.__name=name
        pass

    # def get_action(self,hisotry):
    #     pass

    def get_name(self):
        print("The player's name is ",self.__name,"!")

# class RandomPlayer(Player):
#     def get_action(self,history,card):
#         a=random.choice(range(self.NUM_ACTIONS))
#         return self.ACTIONS[a]

class CFRPlayer(Player):
    def __init__(self,name=None):
        Player.__init__(self,name)
        self.nodeMap = {}
        self.util=0

    class Node:
        def __init__(self):
            self.num=CFRPlayer().NUM_ACTIONS
            self.infoSet=None
            self.regretSum=[0 for i in range(self.num)]
            self.strategy=[0 for i in range(self.num)]
            self.strategySum=[0 for i in range(self.num)]

        def getStrategy(self,realizationWeight):
            normalizingSum=0
            for i in range(self.num):
                if self.regretSum[i]>0:
                    self.strategy[i]=self.regretSum[i]
                else:
                    self.strategy[i]=0
                normalizingSum+=self.strategy[i]
            for i in range(self.num):
                if normalizingSum>0:
                    self.strategy[i]/=normalizingSum
                else:
                    self.strategy[i]=1.0/self.num
                self.strategySum[i]+=realizationWeight*self.strategy[i]
            return self.strategy
        def getAverageStrategy(self):
            avgStrategy=[0 for i in range(self.num)]
            normalizingSum=0
            for i in range(self.num):
                normalizingSum+=self.strategySum[i]
            for i in range(self.num):
                if normalizingSum>0:
                    avgStrategy[i]=self.strategySum[i]/normalizingSum
                else:
                    avgStrategy[i]=1.0/self.num
            return avgStrategy
        def toString(self):
            print(self.infoSet+":"+str(self.getAverageStrategy()))

    def play(self):
        self.util+=self.cfr([1,1])

        # infoSet = str(self.cards[self.player]) + self.history
        # node = self.nodeMap.get(infoSet)
        # strategy=node.getStrategy(1)
        # print("strategy:",strategy)
        # pro=random.random()
        # tot=0
        # for i in range(self.NUM_ACTIONS):
        #     tot+=strategy[i]
        #     if pro<tot:
        #         return self.ACTIONS[i]

    def get_avgstr(self):
        print("Average game value:" + str(self.util / iterations))
        for key, value in self.nodeMap.items():
            print('{key}:{value}'.format(key=key, value=value.getAverageStrategy()))

    def cfr(self,p):  #card即玩家拿到的牌
        history=game.history
        cards=game.cards
        lenh=len(history)
        player=lenh%2
        opponent=1-player

        rew=game.is_end([player,opponent])
        if rew!=0:
            return rew

        infoSet=str(cards[player])+history
        node=self.nodeMap.get(infoSet)
        if node==None:
           node=self.Node()
           node.infoSet=infoSet
        strategy=node.getStrategy(p[player])
        util=[0.0 for i in range(self.NUM_ACTIONS)]
        nodeUtil=0
        for i in range(self.NUM_ACTIONS):
            game.update(self.ACTIONS[i])
            if player==0:          #这里不要轻易改动
                util[i]=-self.cfr([p[0]*strategy[i],p[1]])
            else:
                util[i]=-self.cfr([p[0],p[1]*strategy[i]])
            game.withdraw()
            nodeUtil+=strategy[i]*util[i]
        for i in range(self.NUM_ACTIONS):
            regret=util[i]-nodeUtil
            node.regretSum[i]+=p[opponent]*regret
        self.nodeMap[infoSet] = node
        return nodeUtil

if __name__=="__main__":
    player=CFRPlayer("cfr1")
    rewards={}
    game=KuhnPoker()
    iterations=100  #

    for i in range(iterations):
        player.play()
        game.reshuffle()

    player.get_avgstr()