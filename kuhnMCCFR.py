from random import shuffle
import random
import numpy as np
class KuhnPoker:
    def __init__(self):
        self.cards=[1,2,3]
        self.init_game()

    def init_game(self):
        random.shuffle(self.cards)
        self.history=""

    def reshuffle(self):
        self.init_game()

    def curr_player(self):
        return len(self.history)%2

    def is_end(self):
        history=self.history
        lenh = len(history)
        player=lenh%2
        opponent=1-player
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

    # def run(self,players):
    #     play_list=list(range(len(players)))
    #     random.shuffle(play_list)
    #     while 1:    #此处可改成step函数
    #         player=play_list[0]
    #         rew=self.is_end(self.history,play_list)
    #         if rew!=0:
    #             return player,rew
    #         a=players[player].get_action(self.history,self.cards)
    #         #update history
    #         self.update(a)
    #         #update player
    #         play_list=play_list[::-1]   #改用queue管理

    def update(self,action):
        self.history+=str(action)

    def withdraw(self,h):
        self.history=h

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
        self.e=0.6

    class Node:
        def __init__(self,infoSet=None):
            self.num=CFRPlayer().NUM_ACTIONS
            self.infoSet=infoSet
            self.c=0
            self.regretSum=np.zeros(2)
            self.strategySum=np.zeros(2)

        def getStrategy(self):
            pos_r=np.maximum(0,self.regretSum)
            sum_r=np.sum(pos_r)
            strategy=pos_r/sum_r if sum_r>0 else np.ones(2)/2
            return strategy
        def getAverageStrategy(self):
            sum_s=np.sum(self.strategySum)
            avgStrategy=self.strategySum/sum_s if sum_s>0 else np.ones(2)/2
            return avgStrategy
        def toString(self):
            print(self.infoSet+":"+str(self.getAverageStrategy()))

    def play(self,iterations):
        for i in range(iterations):
            for j in range(2):
                # print("turn",i+1)
                # u,tail=self.oscfr(i+1,j,1,1,1) #t,i,p,s
                u=self.escfr(j)
                self.util+=u
                game.reshuffle()

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

        for key in sorted(self.nodeMap.keys()):
            print('{key}:{value}'.format(key=key, value=self.nodeMap[key].getAverageStrategy()))

    # def sample(self,strategy):
    #     p=random.random()
    #     total=0
    #     for i in range(self.NUM_ACTIONS):
    #         total+=strategy[i]
    #         if p<total:
    #             return i

    def oscfr(self,t,i,pi,p_i,s):
        history=game.history
        cards=game.cards
        player=game.curr_player()

        rew=game.is_end()
        if rew!=0:
            if player==i:
                return rew/s,1
            else:
                return -rew/s,1

        infoSet=str(cards[player])+history
        node=self.nodeMap.get(infoSet)
        if node==None:
           node=self.Node(infoSet)
        strategy=node.getStrategy()
        samstra = (np.ones(2) / 2 * self.e + (1 -self.e) * strategy) if player == i else strategy
        a=np.random.choice([0,1],p=samstra)
        # util=[0.0 for i in range(self.NUM_ACTIONS)]
        # nodeUtil=0
        # for i in range(self.NUM_ACTIONS):
        #     game.update(self.ACTIONS[i])
        #     if player==0:
        #         util[i]=-self.cfr([p[0]*strategy[i],p[1]])
        #     else:
        #         util[i]=-self.cfr([p[0],p[1]*strategy[i]])
        #     game.withdraw()
        #     nodeUtil+=strategy[i]*util[i]
        game.update(self.ACTIONS[a])

        if player==i:
            u, tail = self.oscfr(t,i,pi*strategy[a],p_i, s * samstra[a])
            w = u * p_i
            for m in range(self.NUM_ACTIONS):
                if m==a:
                    regret=w*(tail-tail*strategy[a])   #tail=pi(ha,z)
                else:
                    regret=-w*tail*strategy[a]
                node.regretSum[m]+=regret
        else:
            u, tail = self.oscfr(t,i,pi,p_i*strategy[a], s * samstra[a])
            for m in range(self.NUM_ACTIONS):
                node.strategySum[m]+=p_i*strategy[m]*(t-node.c)
            node.c=t
        self.nodeMap[infoSet] = node
        return u,tail*strategy[a]

    def escfr(self,p):
        player=game.curr_player()
        history=game.history
        cards=game.cards

        rew=game.is_end()
        if rew!=0:
            if player==p:
                return rew
            else:
                return -rew

        infoSet=str(cards[player])+history
        node=self.nodeMap.get(infoSet)
        if node==None:
            self.nodeMap[infoSet]=self.Node(infoSet)
        node=self.nodeMap[infoSet]

        strategy=node.getStrategy()
        import copy
        h=copy.deepcopy(history)
        if player==p:
            u=np.zeros(self.NUM_ACTIONS)
            for i in range(self.NUM_ACTIONS):
                game.update(self.ACTIONS[i])
                u[i]=self.escfr(p)
                game.withdraw(h)
            u_e=np.sum(strategy*u)
            node.regretSum+=u-u_e
            return u_e
        else:
            a=np.random.choice([0,1],p=strategy)
            game.update(self.ACTIONS[a])
            u=self.escfr(p)
            node.strategySum+=strategy
            return u


if __name__=="__main__":
    player=CFRPlayer("cfr1")
    game=KuhnPoker()
    iterations=pow(10,5) #
    player.play(iterations)
    # for i in range(iterations):
    #     player.play()
    #     game.reshuffle()
    player.get_avgstr()