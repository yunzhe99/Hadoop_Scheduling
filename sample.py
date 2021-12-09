# 按 按两次 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。

import numpy as np
import copy
import random
import env
import tools

# rank[jobID][blockID][coreID]储存block序
# ftCore=[]每个核上数据块的最后结束时间
# n=5# job总数
#a = 0.02  # 处理速度计算的参数
# m=10# 总核数

'''
模块使用方法:先调用sol_init(n, m, block, max_k)方法生成一个随机解，然后调用sample
'''

def init_job(coreNumber, k):
    # coreNumber:使用的核数  k:job(i)的block数量

    sol = [[] for c in range(coreNumber)]
    rank = [[0 for k in range(k)] for c in range(coreNumber)]
    i = 0  # core下标
    j = 0  # block下标
    while j < k:
        sol[i] += [j]
        rank[i][j] = len(sol[i])  # 该job在第i个分配core上block[k]的序
        i = (i + 1) % coreNumber
        j += 1
    return sol


def sol_init(n, m, block, max_k):
    # 初始化一个随机解，n是job数，m是核数，block是每个job的block数，max_k是块最多job的块数
    rank = [[[0 for i in range(n)] for k in range(max_k)] for c in range(m)]  # X(j,k,i)
    job_rank = [[0 for i in range(n)] for c in range(m)]
    total_sol = [[] for core in range(m)]  # 总的直观block编号图
    job_schedule = []  # 所有job的block分配方案
    job_order = [[] for core in range(m)]  # 每个核上以job为单位的序
    solution = {'CoreNumber': [], 'JobOrder': []}  # e,p形式的解

    for i in range(n):
        solution['JobOrder'].append(i + 1)
        cores = random.randint(1, min(10, m, len(block[i])))
        solution['CoreNumber'].append(cores)
        job_sol = init_job(cores, len(block[i]))
        dict_job = {'cores': cores, 'scheme': job_sol, 'core_id': []}
        job_schedule.append(dict_job)
        core_set = set([])
        for j in range(cores):  # j表示job分配的核下标
            while True:
                c = random.randint(0, m - 1)
                if not c in core_set:
                    break
            core_set.add(c)
            dict_job['core_id'].append(c)
            job_order[c].append([i, j])
            job_rank[c][i] = len(job_order[c])
            for k in job_sol[j]:
                total_sol[c].append([i, k])
                rank[c][k][i] = len(total_sol[c])

    return job_schedule, solution['JobOrder']


def check(job_schedule, job_order):
    return True


def sample_change(job_schedule, job_order, m, n):
    '''

    :param job_schedule: The core arrangement of each job's block
    :param job_order: The priority of job
    :param m: 核心数量
    :param n: job数量
    :return: 进行一次随机变换之后的(schedule, order)解
    '''
    schedule = copy.deepcopy(job_schedule)
    order = copy.deepcopy(job_order)

    if random.randint(0, 2) == 0 and n >= 2:
        i = random.randint(0, n - 2)  # suppose n>=2
        order[i], order[i + 1] = order[i + 1], order[i]

    if random.randint(0, 2) != 0 and m > 1:
        jobID = random.randint(0, n - 1)
        job = schedule[jobID]
        core_set = set([i for i in job['core_id']])
        i = random.randint(0, job['cores'] - 1)
        core1 = job['core_id'][i]
        while len(core_set) != m:
            core1 = random.randint(0, m - 1)
            if not core1 in core_set:
                break
        job['core_id'][i] = core1

    if random.randint(0, 3) != 0:
        jobID = random.randint(0, n - 1)
        job = schedule[jobID]
        if not (job['cores'] == 1 and len(job['scheme'][0]) == 1):
            pre = random.randint(0, job['cores'] - 1)
            flag = random.randint(0, len(job['scheme'][pre]) - 1)
            bk = job['scheme'][pre][flag]
            while True:
                now = random.randint(0, min(job['cores'], 9, m-1))
                if now != pre:
                    break

            if not(len(job['scheme'][pre]) == 1 and now == job['cores']):
                if len(job['scheme'][pre]) == 1:
                    job['cores'] -= 1
                    job['scheme'][now].append(bk)
                    del job['scheme'][pre]
                    del job['core_id'][pre]


                elif now == job['cores']:
                    job['cores'] += 1
                    job['scheme'].append([bk])
                    job['scheme'][pre].remove(bk)
                    core_set = set([i for i in job['core_id']])
                    while True:
                        core1 = random.randint(0, m - 1)
                        if not core1 in core_set:
                            break
                    job['core_id'].append(core1)

                else:
                    job['scheme'][pre].remove(bk)
                    job['scheme'][now].append(bk)

    if check(schedule, order):
        return schedule, order
    else:
        return job_schedule, job_order

def solution_map(order, schedule, m, max_k):
    '''
    :return: (order,schedule)解映射到X(j,k,i)解
    '''
    num=[ 0 for i in range(m) ]
    rank = np.zeros((m, max_k, len(order)))
    for i in order:
        job = schedule[i-1]
        for j in range(job['cores']):
            c=job['core_id'][j]
            for k in job['scheme'][j]:
                num[c]+=1
                rank[c][k][i-1]=num[c]
    return rank

def sample(schedule, order, m, n, max_k, t):
    '''

    :param schedule: 各job的block分配
    :param order:  job schedule的优先级
    :param m:  core数
    :param n:  job数
    :param max_k: block最多的job的block数
    :param t:  循环次数
    :return:  X(j,k,i)解
    '''
    for i in range(t):
        schedule, order=sample_change(schedule, order, m, n)
    '''
    print(order)
    for item in schedule:
        print(item)
    '''
    return solution_map(order, schedule, m, max_k)

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    #block = [[1, 1, 1], [2, 3, 2, 2], [4, 4, 4]]
    #job_schedule, job_order = sol_init(3, 5, block, 4)
    rs = env.ResourceScheduler()
    n = rs.numJob
    m = rs.hostCore[0]
    max_k = max(rs.jobBlock)
    job_schedule, job_order = sol_init(n, m, rs.dataSize, max_k)
    #schedule, order = sample_change(job_schedule, job_order, m, n)

    '''
    print(job_order)
    for item in job_schedule:
        print(item)
    '''
    #测试了1000次近似解生成，没有报错
    rank=sample(job_schedule, job_order, m, n, max_k, 1000)

    #print(rank)
