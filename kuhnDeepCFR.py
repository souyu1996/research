import random
from kuhnCFR import Player
from kuhnCFR import KuhnPoker as Game
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as DATA
class Net(nn.Module):
    def __init__(self):
        super(Net,self).__init__()
        self.fc1=nn.Linear(5,64)
        self.fc2=nn.Linear(64,84)
        self.fc3=nn.Linear(84,2)

    def forward(self,x):
        x=F.relu(self.fc1(x))
        x=F.relu(self.fc2(x))
        x=self.fc3(x)
        return x

    def num_flat_features(self,x):
        size=x.size()[1:]
        num_features=1
        for s in size:
            num_features*=s
        return num_features


class CFRPlayer(Player):
    def __init__(self,name=None):
        Player.__init__(self, name)
        self.net=[Net() for i in range(2)]
        self.max_length=pow(10,2)
        self.advantage =[[] for i in range(2)]
        self.strategy=[]
        self.count=[0 for i in range(3)]
        self.K=10

    def train(self,iterations):
        for t in range(1,iterations+1):
            print("iteration",t)
            for p in range(2):
                for k in range(self.K):
                    print("epoch",k)
                    print("game:",game.cards)
                    self.deepcfr(p,t)
                    game.reshuffle()
                self.deepnn(self.net[p],self.advantage[p])
        net=Net()
        self.deepnn(net,self.strategy)
        return net   #这里返回什么

    def deepnn(self,net,data):
        net=net.float()
        data=np.array(data)
        optimizer = optim.SGD(net.parameters(), lr=0.001)
        input = torch.from_numpy(data[:, :5])
        weight = torch.from_numpy(data[:, 5])
        target = torch.from_numpy(data[:, 6:])
        torch_data = DATA.TensorDataset(input,weight,target)
        loader = DATA.DataLoader(dataset=torch_data, batch_size=5, shuffle=True, num_workers=2)
        for epochs in range(10):
            for step, (batch_x,batch_w, batch_y) in enumerate(loader):
                output = net(batch_x.float())
                optimizer.zero_grad()
                batch_w=batch_w.view(1,-1)
                loss = torch.mean(torch.mm(batch_w,torch.pow(batch_y - output, 2)))
                loss.backward()
                optimizer.step()

    def traverse(self,input):
        indexmap={'p':0,'b':1,'pb':2,'':3}
        ind=indexmap[input]
        return np.eye(4)[ind]

    def reservior_sample(self,memory,data,count):
        # if np.zeros(8) in memory:
        #     ind=np.argwhere((memory==np.zeros(8)).all(1))[0][0]
        # else:
        #     ind=np.random.choice(range(self.max_length))    #修改一下
        if count>=self.max_length:
            ind=random.randint(count)
            if ind<self.max_length:

                memory[ind]=data
        else:
            memory.append(data)

    def regret_matching(self,input,net):
        input=torch.from_numpy(input)
        output=net(input.float())
        advantage=output.data.numpy()
        pos_r=np.maximum(0,advantage)
        sum_r=np.sum(pos_r)
        strategy = pos_r / sum_r if sum_r > 0 else np.ones(2) / 2
        return strategy

    def deepcfr(self,p,t):
        player = game.curr_player()
        history=game.history
        cards = game.cards

        rew = game.is_end()
        if rew != 0:
            if player == p:
                return rew
            else:
                return -rew
        infoSet=np.append(np.array([cards[player]]),self.traverse(history))
        print(game.history)
        import copy
        h = copy.deepcopy(history)
        if player == p:
            strategy = self.regret_matching(infoSet,self.net[player])  # 用到网络训练
            u = np.zeros(self.NUM_ACTIONS)
            for i in range(self.NUM_ACTIONS):
                game.update(self.ACTIONS[i])
                u[i] = self.deepcfr(p,t)
                game.withdraw(h)
            u_e = np.sum(strategy * u)
            print("util:",u,"avg util:",u_e)
            regret=u-u_e
            unit=np.concatenate((infoSet,np.array([t]),regret)).tolist()
            self.reservior_sample(self.advantage[player],unit,self.count[player])
            print(player,self.advantage[player])
            return u_e
        else:
            strategy = self.regret_matching(infoSet,self.net[player])  # 用到网络训练
            a = np.random.choice([0, 1], p=strategy)
            game.update(self.ACTIONS[a])
            unit=np.concatenate((infoSet,np.array([t]),strategy)).tolist()
            self.reservior_sample(self.strategy,unit,self.count[2])
            return self.deepcfr(p,t)


if __name__=="__main__":
    player = CFRPlayer("cfr1")
    game = Game()
    iterations = pow(10, 1)  #
    net=player.train(iterations)
    for i in [1,2,3]:
        for j in ['','p','b','pb']:
            infoSet = np.append(np.array([i]), player.traverse(j))
            print(i,j,player.regret_matching(infoSet,net)) # 用到网络训练


