import numpy as np
import matplotlib.pyplot as plt


class SAoptimizer:
    def __init__(self):
        super().__init__()

    def optimize(self, f, ybound=(-np.inf, np.inf), initf=np.random.random, randf=np.random.random,
            t=1000, alpha=0.98, stop=0.001, iterPerT=1, l=1):
        '''
        :param f: 目标函数,接受np.array作为参数 
        :param ybound: y取值范围 
        :param initf: 目标函数的初始权值函数，返回np.array 
        :param alpha: 退火速率  
        :param iterPerT: 每个温度下迭代次数 
        :param t: 初始温度 
        :param l:新旧值相减后的乘数，越大，越不容易接受更差值
        :param stop: 停火温度 
        :param randf: 对参数的随机扰动函数，接受现有权值，返回扰动后的新权值np.array
        '''
        #初始化
        y_old = None
        while y_old == None or y_old < ybound[0] or y_old > ybound[1]:
            x_old = initf()
            y_old = f(x_old) 
        y_best = y_old
        x_best = np.copy(x_old)       
        #降温过程
        count = 0
        while(t > stop):
            downT = False
            for i in range(iterPerT):
                x_new = randf(x_old)
                y_new = f(x_new)    
                if y_new > ybound[1] or y_new < ybound[0]:
                    continue
                #根据取最大还是最小决定dE,最大为旧值尽可能小于新值
                dE = (y_old - y_new) * l
                if dE < 0: 
                    downT = True
                    count = 0
                else: count += 1
                if self.__judge__(dE, t):
                    x_old = x_new
                    y_old = y_new
                    if y_old < y_best:
                        y_best = y_old
                        x_best = x_old
            if downT:
                t = t * alpha
            #长时间不降温
            if count > 1000: break
        self.weight = x_best
        return x_best, y_best
    
    def __judge__(self, dE, t):
        '''
        :param dE: 变化值
        :t: 温度
        根据退火概率: exp((E1-E2)/T)，决定是否接受新状态
        '''
        if dE < 0:
            return 1
        else:
            p = np.exp(-dE / t)
            import random
            
            if p > np.random.random(size=1):
                return 1
            else: return 0
