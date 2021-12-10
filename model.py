import numpy as np
from env import ResourceScheduler
from sample_fun import sol_init, sample, solution_map
from tools import maxtf_job

def __judge__(dE, t):
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

def optimize(rs, ybound=(0, np.inf), t=1000, alpha=0.98, stop=0.001, iterPerT=1, l=1):
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
    # 初始化
    y_old = None
    m=rs.m
    n=rs.numJob
    max_k=rs.max_k
    while y_old == None or y_old < ybound[0] or y_old > ybound[1]:
        schedule, order = sol_init(rs.numJob, rs.m, rs.dataSize, rs.max_k)
        x_old = solution_map(order, schedule, rs.m, rs.max_k)
        y_old = maxtf_job(x_old, rs)
    y_best = y_old
    x_best = np.copy(x_old)
    # 降温过程
    count = 0
    while  t > stop:
        downT = False
        for i in range(iterPerT):
            schedule, order, x_new=sample(schedule, order, m, n, max_k, 1)
            y_new = maxtf_job(x_new, rs)
            if y_new > ybound[1] or y_new < ybound[0]:
                continue
            # 根据取最大还是最小决定dE,最大为旧值尽可能小于新值
            dE = (y_old - y_new) * l
            if dE < 0:
                downT = True
                count = 0
            else: count += 1
            if __judge__(dE, t):
                x_old = x_new
                y_old = y_new
                if y_old < y_best:
                    y_best = y_old
                    x_best = x_old
        if downT:
            t = t * alpha
        # 长时间不降温
        if count > 1000: break
    return x_best, y_best

if __name__ == '__main__':
    rs = ResourceScheduler(taskType=1, caseID=2)
    # print(m)
    y_best=np.inf
    x_best=[]
    for i in range(1):
        x, y = optimize(rs, ybound=(0, np.inf), t=1, alpha=0.98, stop=0.001, iterPerT=1, l=1)
        if y < y_best:
            y_best=y
            x_best=x
        
    print(y_best)
    print(x_best)