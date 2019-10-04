import random
from random import choice
import copy
import unittest

class Poker:
    def __init__(self):
        self.cards={1,2}#,6,7,8,9
        self.num_per_color=4
        self.action_set=[0,1,2,11,22]#,6,7,8,9,11,22,33,44,55,66,77,88,99,111,222,333,444,555,666,777,888,999
        self.players=['A','B','C','D']
        self.teams=[['A','C'],['B','D']]

    def init_game(self):
        card = [i for i in self.cards] * self.num_per_color
        self.state = {}
        self.player_state={i:False for i in self.players}
        self.history = ['',0,[]]
        self.reward={}
        self.possible_actions=self.action_set[1:]
        self.action_profile=self.action_set[1:]
        while card:
            index = random.randint(0,len(card)-1)
            x = card.pop(index)
            player=self.get_player()
            if player in self.state:
                self.state[player]+=[x]
            else:
                self.state[player]=[x]
        for i in self.players:
            self.state[i].sort()
        print(self.state)

    def state_update(self,action,player):
        if self.state[player]==[]:
        #    print(self.player_state)
            return
        action0 = list(str(action))
        state = [str(i) for i in self.state[player]]
        if self.is_subset(action0, state):
            for i in action0:
                self.state[player].remove(int(i))
        if  self.state[player]==[]:
            print("Player " + str(player) + " plays out his cards!")
        print("now players' state:",self.state)

    def is_subset(self,l,r):
        a=copy.deepcopy(l)
        b=copy.deepcopy(r)
        for i in range(len(a)):
            if a[i] in b:
                b.remove(a[i])
                if i == len(a) - 1:
                    return True
            else:
                return False

    def is_accessible(self,action):  ##action是否可行   playing rule
        diff=action-self.history[1]
        print("diff:",diff)
        if self.history[1]==0:
            return True
        if  1<=self.history[1]<=9 and 1<=action<=9:
            if 1<=diff<=8:
                return True
        elif 11<=self.history[1]<=99 and 11<=action<=99:
            if diff%11==0 and 9>diff//11>0:
                return True
        elif 111<=self.history[1]<=999 and 111<=action<=999:
            if diff%111==0 and 9>diff//111>0:
                return True
        else:
            return False

    def possible_action(self,player):
        if player == self.history[0] or self.history[0] == '':
            self.action_profile = self.action_set[1:]
        else:
            action_index = self.action_set.index(self.history[1])
            print("index:",action_index)
            a = []
            for i in range(action_index + 1, len(self.action_set)):
                print("actions set:",self.action_set[i])
                if self.is_accessible(self.action_set[i]):
                    a.append(self.action_set[i])
            self.action_profile = a
        print(self.action_profile)


    def action_update(self,player):
        self.possible_action(player)
        action=[]
        state = self.state[player]
        state0=[str(i) for i in state]
        for i in range(len(self.action_profile)):
            l = list(str(self.action_profile[i]))
            if self.is_subset(l,state0):
                action.append(self.action_profile[i])
        if player!=self.history[0] and self.history[0]!='':
            action.append(0)
        self.possible_actions=action
        print("now available actions",self.possible_actions)

    def simulate(self):
        pass

    def history_update(self,action,player):
        if self.history[0] == player and action == 0:
            self.history[0] = ''
            self.history[1] = 0
        elif self.history[0] == '' and action == 0 and self.state[player] == []:
            self.history[0] = ''
        elif self.history[0] == '' and action!=0 or self.is_accessible(action) or self.history[0] == player and action != 0:
            self.history[0] = player
            self.history[1] = action
        self.history[2].append(action)
        print("now playing history:",self.history)
        if self.history[0]!='' and self.history[1]==0:
            exit()

    def update(self,action,player):
        self.state_update(action, player)
        self.history_update(action, player)

    def get_player(self):
        p = self.players.pop(0)
        self.players.append(p)
        return p

    def init_player(self):
        index=choice(len(self.players))
        for i in range(index):
            p = self.players.pop(0)
            self.players.append(p)
        return self.players[index]

    def play(self,poker):
        #player=self.init_player()
        self.init_game()
        pl={}
        ai=MCCFR(poker)
        human=Human(poker)
        rand0=Random(poker)
        rand1=Random(poker)
        rand2=Random(poker)
        rand3=Random(poker)
        pl['A']=ai
        pl['B']=rand1
        pl['C']=rand2
        pl['D']=rand3
        while 1:
            player=self.get_player()
            print("now playing player:"+player)
            self.action_update(player)
            if self.possible_actions==[] or self.possible_actions==[0]:
                action=0
            else:
                action=pl[player].get_action()
            #action=self.possible_actions[action]
            self.action_print(action, player)

            self.update(action,player)
            end=self.is_win(player)
            if end:
                print("Player "+str(player)+"'s team wins!")

                if self.reward['A']>0:
                    print(self.reward)
                    return 1
                else:
                    return 0
                break

    def is_win(self,player):
        index=self.players.index(player)
        opponent1=self.players[(index+1)%4]
        partner=self.players[(index+2)%4]
        opponent2=self.players[(index+3)%4]
        if self.state[player] == [] and self.state[partner] == []:
            if self.state[opponent1] != [] and self.state[opponent2] != []:
                print("aaa")
                self.reward[player] = 2    #1.5
                self.reward[partner] = 2   #2.5
                self.reward[opponent2] = self.reward[opponent1] = -2
                return True
            elif self.state[opponent1] == [] or self.state[opponent2] == []:
                print("bbb")
                self.reward[player] = 1    #0.5
                self.reward[partner] = 1        #1.5
                self.reward[opponent1] = self.reward[opponent2] = -1
                return True   #self.player?player
        elif self.state[opponent1]==[] and self.state[opponent2]==[]:
            if self.state[player]!=[] and self.state[partner]!=[]:
                self.reward[player]=self.reward[partner]=-2
                self.reward[opponent2]=self.reward[opponent1]=2
                return True
            elif self.state[player]==[] or self.state[partner]==[]:
                self.reward[player]=self.reward[partner]=-1
                self.reward[opponent1]=self.reward[opponent2]=1
                return True
        else:
            return False

    def action_print(self,action,player):
        print('{player}:{action}'.format(player=player,action=action))

class Random:
        def __init__(self,poker):
            self.poker=poker

        def get_action(self):   ##从行动集中获取随机的行为
            actions=self.poker.possible_actions
            action_num=len(actions)
            if action_num==0:
                return 0
            else:
                action=random.randint(0,action_num-1)
                return actions[action]


        def __str__(self):
            return "Random Player"

class Human:
    def __init__(self,poker):
        self.poker=poker

    def get_action(self):
        actions=self.poker.possible_actions
        print(actions)
        print("Your turn!!!")
        souyu=int(input())
        for i in range(len(actions)):
            if actions[i]==souyu:
                break
            elif i>=len(actions)-1:
                exit()
        return souyu

class MCCFR:
        def __init__(self, poker):
            self.poker = poker
            self.action_set=poker.action_set
            self.teams=poker.teams
            self.cards =poker.cards
            self.num_per_color = self.poker.num_per_color
            self.nodeMap={}
            self.reward={}

        class Node:
            def __init__(self,num):  #actions
                self.infoSet = None

                self.num=num
                self.regretSum = [0 for i in range(self.num)]
                self.strategy = [0 for i in range(self.num)]
                self.strategySum = [0 for i in range(self.num)]
            #    self.possible_actions=copy.deepcopy(actions)
            #    self.num=len(self.possible_actions)

            def getStrategy(self, weight):
                normalizingSum = 0
                for i in range(self.num):
                    if self.regretSum[i]>0:
                        self.strategy[i]=self.regretSum[i]
                    else:
                        self.strategy[i]=0
                    normalizingSum+=self.strategy[i]
                for i in  range(self.num):
                    if normalizingSum>0:
                        self.strategy[i]/=normalizingSum
                    else:
                        self.strategy[i]=1.0/self.num
                    self.strategySum[i]=weight*self.strategy[i]
                return self.strategy


            def getAverageStrategy(self):            #根据每个信息集汇总还是根据整个游戏的发生概率？
            #    action_num=len(self.possible_actions)
                avgStrategy = [0 for i in range(self.num)]
                normalizingSum = 0
                for i in range(self.num):
                    normalizingSum += self.strategySum[i]
                for i in range(self.num):
                    if normalizingSum > 0:
                        avgStrategy[i] = self.strategySum[i] / normalizingSum
                    else:
                        avgStrategy[i] = 1.0 / self.num
                return avgStrategy

        def card_init(self):  ##发牌
            states = {}
            self.history = copy.deepcopy(self.history_init)
            #history=self.history[2]
            self.player_state = copy.deepcopy(self.player_state_init)
            self.play_order = copy.deepcopy(self.players_init)
            player_set=[]
            self.state=copy.deepcopy(self.state_init)
            self.player=copy.deepcopy(self.player_init)
            #pl=copy.deepcopy(self.players)
    #        print(self.state)
            for i in self.play_order:  # 发牌对象
                if self.state[i]!=[] and i != self.player:
                    player_set.append(i)
                if self.state[i]==[]:
                    states[i]=[]
        #    print(pl)
            states[self.player] = self.state[self.player]
            card = [i for i in self.cards] * self.num_per_color
            if self.history[2]!=[]:            #去除history中已出的牌
                for i in self.history[2]:
                    while i>10:
                        if i%10 in card:
                            card.remove(i%10)
                        i=i//10
                    if i in card:
                        card.remove(i)
            if states[self.player]!=[]:         #去除模拟玩家已知的牌
                for i in states[self.player]:
                    card.remove(i)
            player_num = {i: 0 for i in player_set}
            for i in card:
                p=choice(player_set)
                while player_num[p]>=len(self.state[p]):
                    p=choice(player_set)
                if p in states:
                    states[p].append(i)
                else:
                    states[p]=[i]
                player_num[p]+=1
        #    print(pl)
        #    print(self.player_state)
            for pla in player_set:
                if pla in player_set:
                    states[pla].sort()
            print(states)
            return states

        def is_accessible(self, action):  ##action是否可行   playing rule
            diff = action - self.history[1]
            print("diff:",diff)
            if self.history[1]==0:
                return True
            if 1 <= self.history[1] <= 9 and 1 <= action <= 9:
                if 1 <= diff <= 8:
                    return True
            elif 11 <= self.history[1] <= 99 and 11 <= action <= 99:
                if diff % 11 == 0 and 9 > diff // 11 > 0:
                    return True
            elif 111 <= self.history[1] <= 999 and 111 <= action <= 999:
                if diff % 111 == 0 and 9 > diff // 111 > 0:
                    return True

            return False

        def is_subset(self, l, r0):
            r=copy.deepcopy(r0)
            for i in range(len(l)):
                if l[i] in r:
                    r.remove(l[i])
                    if i == len(l) - 1:
                        return True
                else:
                    return False

        def card_update(self, action, player):
            if self.card_state[player]==[]:
                print(self.player_state)
                return
            action0 = list(str(action))
            state = [str(i) for i in self.card_state[player]]
            if self.is_subset(action0, state):
                for i in action0:
                    self.card_state[player].remove(int(i))
            self.player_state_update(player)
            if  self.card_state[player]==[]:
                print("Player " + str(player) + " plays out his cards!")
            print("now playing state is:",self.card_state)
               # self.player_state[player] = True

        def player_state_update(self,player):
            if self.card_state[player]==[]:
                self.player_state[player]=True

        def possible_action(self, player):
            if player == self.history[0] or self.history[0] == '':
                self.action_profile = self.action_set[1:]
            else:
                action_index = self.action_set.index(self.history[1])
                a = []
                for i in range(action_index + 1, len(self.action_set)):
                    if self.is_accessible(self.action_set[i]):
                        a.append(self.action_set[i])
                self.action_profile = a
            print("now action profile is:",self.action_profile)

        def action_update(self, player):
            self.possible_action(player)
            action = []
            state = self.card_state[player]
            state0 = [str(i) for i in state]
            for i in range(len(self.action_profile)):
                l = list(str(self.action_profile[i]))
                if self.is_subset(l, state0):
                    action.append(self.action_profile[i])
            if player!=self.history[0] and self.history[0]!='':
                action.append(0)
            self.actions = action
            print("now available actions:",self.actions)

        def history_update(self, action, player):
            if self.history[1]==0 and action==0:
                self.history[0]=''
            elif self.history[0]==player and action==0:
                self.history[0]=''
                self.history[1]=0
            elif self.history[0]=='' and action==0 and self.card_state[player]==[]:
                self.history[0]=''
            elif self.history[0] == '' and action!=0 or self.is_accessible(action) or self.history[0] == player and action!=0:
                self.history[0] = player
                self.history[1] = action
            self.active_action.append(self.history[1])
            self.active_player.append(self.history[0])
            self.history[2].append(action)
            print("now active action set:",self.active_action)
            print("now active player set:",self.active_player)
            print("now playing history:", self.history)
            if self.history[0] != '' and self.history[1] == 0:
                exit()

        def next_player(self):
            p=self.play_order.pop(0)
            self.play_order.append(p)
            return p

        def is_play_out(self,player,partner,opponent1,opponent2):
            if self.card_state[player] == [] and self.card_state[partner] == []:
                if self.card_state[opponent1] != [] and self.card_state[opponent2] != []:
                    print("aaa")
                    self.reward[player] = 2    #1.5
                    self.reward[partner] = 2   #2.5
                    self.reward[opponent2] = self.reward[opponent1] = -2
                    print("player ",player,"'s team wins!!!")
                    return True
                elif self.card_state[opponent1] == [] or self.card_state[opponent2] == []:
                    print("bbb")
                    self.reward[player] = 1    #0.5
                    self.reward[partner] = 1        #1.5
                    self.reward[opponent1] = self.reward[opponent2] = -1
                    print("player ",player,"'s team wins!!!")
                    return True   #self.player?player
            elif self.card_state[opponent1]==[] and self.card_state[opponent2]==[]:
                if self.card_state[player]!=[] and self.card_state[partner]!=[]:
                    self.reward[player]=self.reward[partner]=-2
                    self.reward[opponent2]=self.reward[opponent1]=2
                    print("player ",opponent1,"'s team wins!!!")
                    return True
                elif self.card_state[player]==[] or self.card_state[partner]==[]:
                    self.reward[player]=self.reward[partner]=-1
                    self.reward[opponent1]=self.reward[opponent2]=1
                    print("player ",opponent2,"'s team wins!!!")
                    return True
            else:
                return False

        def train(self, iterations):
            util = 0
            for i in range(iterations):
                print("Simulation  TRUN  "+str(i+1))
                self.card_state = self.card_init()
    #            print(self.card_state)
                self.visited_action=[]
                self.active_action=[copy.deepcopy(self.history[1])]
                self.active_player=[copy.deepcopy(self.history[0])]
                util += self.cfr(self.card_state,self.history,self.player, [[1, 1], [1, 1]])  # 传入每名玩家的牌的状态,历史记录和到达这个节点的概率
            print("Average game value:" + str(util / iterations))
            for key, value in self.nodeMap.items():
                print('{key}:{value}'.format(key=key, value=value.getAverageStrategy()))

        def cfr(self,card,history,player,p):
            #print(self.visited_action)
            if self.card_state[player]==[]:
                self.actions=[0]
            else:
                self.action_update(player)
            actions=[]
            for i in self.actions:
                actions.append(i)
            #actions=a_set

            index=self.players_init.index(player)
            print("now playing player:",player)
            print("now available actions:"+str(actions))

            #index = self.play_order.index(player)
            opponent1 =self.players_init[(index+1)%4]
            partner = self.players_init[(index+2)%4]
            opponent2 = self.players_init[(index+3)%4]

            if self.is_play_out(player, partner, opponent1, opponent2):
                print("rewards:",self.reward)
                return self.reward[player]

            ca=[str(i) for i in card[player]]
            his=[str(i) for i in history[2]]
            infoSet = "".join(ca)+" "+"".join(his)
            print("now infoset:",infoSet)
            node = self.nodeMap.get(infoSet)

            if node == None:
                node = self.Node(len(actions))  #infoSet下可行的行动
                node.infoSet = infoSet
                self.nodeMap[infoSet] = node
            else:
                print("There already has one infoset in the map!!!",infoSet,node.strategy)
            pb=0
            if player == self.teams[0][0]:
                pb = copy.deepcopy(p[0][0])
            elif player == self.teams[1][0]:
                pb = copy.deepcopy(p[1][0])
            elif player == self.teams[0][1]:
                pb = copy.deepcopy(p[0][1])
            elif player == self.teams[1][1]:
                pb = copy.deepcopy(p[1][1])

            if node.num!=len(actions):
                print("The node's actions is not same!",node.strategy,actions)
                exit()
            strategy = node.getStrategy(pb)

            util = [0.0 for i in range(len(actions))]

            nodeUtil = 0

            for i in range(len(actions)):
                print("run "+str(i+1)+"/"+str(len(actions)))
                if i>0:
                    index=len(self.history[2])%4
                    player=self.players_init[(index+3)%4]    #BCDA  the player after recovery
                l=len(self.card_state[player])
                print("player "+str(player)+" plays "+str(actions[i]))
                self.card_update(actions[i],player)    #card state update
                print("*******")

                if l==len(self.card_state[player]) and actions[i]!=0:
                    print("states are not updated!!!")
                    exit()
                self.history_update(actions[i],player)   #history update

                if player == self.teams[0][0]:         #update probability
                    p[0][0] = pb*strategy[i]
                elif player == self.teams[1][0]:
                    p[1][0]=pb*strategy[i]
                elif player == self.teams[0][1]:
                    p[0][1]=pb*strategy[i]
                elif player == self.teams[1][1]:
                    p[1][1]=pb*strategy[i]

                print("pro of this item complishing:  ",p)

                index=self.players_init.index(player)
                player=self.players_init[(index+1)%4]         #player update

                util[i] = -1*self.cfr(card,history,player, p)   #recursion

                print("the value of this action",util[i])
                nodeUtil += strategy[i] * util[i]

                #traceback

                index=len(self.history[2])%4
                player=self.players_init[(index+2)%4]       #BCDA      加testcase

                print("recovery to player:",player)
                if len(self.history[2])>0:
                    h=self.history[2].pop(-1)
                    #self.visited_action.append(h)
                    if h>0:
                        while h>10:
                            self.card_state[player].append(h%10)
                            h=h//10
                        self.card_state[player].append(h)
                        self.card_state[player].sort()
                        print("recovery to state: ",self.card_state)
                if len(self.active_action)>1:
                    self.active_action.pop(-1)
                    self.history[1]=self.active_action[-1]
                    self.active_player.pop(-1)
                    self.history[0]=self.active_player[-1]
                else:
                    if len(self.active_action)==1:
                        self.active_action.pop(-1)
                        self.active_player.pop(-1)
                    self.history[0]=''
                    self.history[1]=0
                print("recovery to active action set:",self.active_action)
                print("recovery to active player set:",self.active_player)
                print("recovery to history:",self.history)

                if strategy[i]>0:
                    if player == self.teams[0][0]:         #update probability
                        p[0][0] /= strategy[i]
                    elif player == self.teams[1][0]:
                        p[1][0]/=strategy[i]
                    elif player == self.teams[0][1]:
                        p[0][1]/=strategy[i]
                    elif player == self.teams[1][1]:
                        p[1][1]/=strategy[i]
                print("recovery to probability:",p)

            for i in range(len(actions)):
                regret = util[i] - nodeUtil
                pro = 1
                x=len(p)
                y=len(p[0])
                for j in range(x):
                    for k in range(y):
                        if self.teams[j][k] != player:
                            #if p[j][k]>0:
                            pro *= p[j][k]
                node.regretSum[i] += pro * regret
            print("this node's util is:"+str(nodeUtil))
            print("node:",node.infoSet,node.strategy)
            self.nodeMap[infoSet] = node
            return nodeUtil

        def get_action(self):
            print("---------------------------AI Plays----------------------------------")
            self.actions = copy.deepcopy(self.poker.possible_actions)       ##特定玩家的动作集
            self.action_profile=copy.deepcopy(self.poker.action_profile)    ##上名玩家出完牌后可能的动作集
            self.state_init = copy.deepcopy(poker.state)                    # 牌的初始状态
            self.player_state_init = copy.deepcopy(poker.player_state)      ##玩家是否出完牌的状态
            self.player_init = copy.deepcopy(self.poker.players[3])         ##初始当前玩家
            self.history_init = copy.deepcopy(self.poker.history)           ##初始历史
            self.players_init = copy.deepcopy(poker.players)                ##玩家列表顺序

            iterations = 1
            self.train(iterations)
            ca=[str(i) for i in self.state_init[self.player_init]]   #进行模拟玩家的牌
            his=[str(i) for i in self.history_init[2]]
            node = self.nodeMap.get("".join(ca)+" "+"".join(his))     #进行模拟的节点
            if node==None:
                return 0

            strategy = node.getAverageStrategy()
        #    print(strategy)
            p = random.random()
            sum = 0

            for i in range(len(strategy)):
                sum += strategy[i]
                if p <= sum:
                    print("-----------------------over-----------------------")
                    return self.poker.possible_actions[i]

        def __str__(self):
            return "AI Player"
##random 0.625
##card={1,2}
##MCCFR iterations=1   winning rate=0.644
##MCCFR iterations=10  winning rate=
##MCFR iterations=100 winning rate=

##card={1,2,3,4,5}
##MCCFR iterations=1 winning rate=
##MCCFR iterations=100 winning rate=

class TestMathFunc(unittest.TestCase):
    def Poker_history_update_test(self):
        pass
if __name__=="__main__":
    iterations=1000
    sum=0
    for i in range(iterations):
        print("TURN "+str(i+1))
        print("-----------------------------------------------------------------")
        poker = Poker()
        sum+=poker.play(poker)
        print(sum)
    print("the winning rate")
    print(sum/iterations)
