import numpy as np
from env import ResourceScheduler

'''
rs = ResourceScheduler(taskType=1, caseID=2)
b=rs.max_k
block_size=rs.dataSize
s_list=rs.Sc
if rs.taskType==2:
    s_t=rs.St
alpha=rs.alpha
block_location=rs.location
core_location=rs.core_location
'''

###############################
# config for case 1
# job * block
# block_size = [[10, 20, 16],
#                 [9, 16],
#                 [10, 6, 20, 15]]
# # 1 * core
# s_list = [5, 5, 5]
# s_t = 40
# alpha = 0.03

# block_location = [[0, 0, 0],
#                     [0, 0],
#                     [0, 0, 0, 0]]

# core_location = [0, 0, 0, 0]

# ###############################
# # config for case 2
# # job * block
# block_size = [[10, 20, 15],
#                 [12, 10, 24],
#                 [18, 20],
#                 [10, 18, 16, 30]]
# # 1 * core
# s_list = [10, 10, 12, 12]
# s_t = 40
# alpha = 0.1

# block_location = [[0, 0, 0],
#                     [1, 1, 1],
#                     [2, 2],
#                     [2, 2, 2, 2]]

# core_location = [0, 0, 1, 1, 2, 2]

# hypterparamters

# c = len(core_location)  # number of cores
# b = 4  # the max number of blocks
# n = len(block_size)  # number of jobs

# the available core time for now
# core_t_list = np.zeros(c)


def on_core(block, core_index, rs):
    return rs.location[block[2]][block[1]] == rs.core_location[core_index]


def tf_core(job_index, core_blocks, core_used, t, core_t_list, rs, core_allocation):
    block_size=rs.dataSize
    core_index = core_blocks[0][0]
    s_list = rs.Sc
    if rs.taskType == 2:
        s_t = rs.St
    alpha=rs.alpha
    # time of finish for a core
    size_core = 0
    size_trans = 0
    for core_block in core_blocks:
        size_block = block_size[core_block[2]][core_block[1]]
        size_core += size_block
        if not on_core(core_block, core_index, rs):
            size_trans += size_block
    if size_trans > 0:
        tp_t = size_trans / s_t
    tp_p = size_core / (s_list[job_index] * (1 - alpha * (len(core_used) - 1)))
    if size_trans > 0:
        tp = tp_t + tp_p
    else:
        tp = tp_p 
    tf = t + tp
    core_t_list[core_index] = tf
    for core_block in core_blocks:
        core_allocation[core_index].append([core_block[2], core_block[1], t, tf])
    return tf


def tf_job(job_index, job_blocks, core_t_list, rs, e, core_allocation):
    # time of finish for a job
    core_used = set()
    for job_block in job_blocks:
        core_used.add(job_block[0])

    e[job_index]=len(core_used)

    # compute t
    t = 0
    for core_index in core_used:
        if t < core_t_list[core_index]:
            t = core_t_list[core_index]
    tf_j = 0
    for core_index in core_used:
        core_blocks = []
        for job_block in job_blocks:
            if job_block[0] == core_index:
                core_blocks.append(job_block)
        tf = tf_core(job_index, core_blocks, core_used, t, core_t_list, rs, core_allocation)
        if tf_j < tf:
            tf_j = tf
    return tf_j


def maxtf_job(X, rs):
    # job order sort

    job_p_list = []
    job_blocks_list = []
    e = [0]*rs.numJob#??????job???????????????
    core=[[0]*rs.max_k for i in range(rs.numJob)]
    core_allocation=[ []for i in range(rs.m) ]

    for job_index in range(X.shape[2]):
        job_blocks = []
        block_p_list = []
        for core_index in range(X.shape[0]):
            for block_index in range(X.shape[1]):
                if X[core_index][block_index][job_index] != 0:
                    job_blocks.append([core_index, block_index, job_index])
                    core[job_index][block_index]=core_index
                    block_p_list.append(X[core_index][block_index][job_index])
        job_p = np.mean(block_p_list)
        job_p_list.append(job_p)
        job_blocks_list.append(job_blocks)
    sorted_id = sorted(range(len(job_p_list)), key=lambda k: job_p_list[k], reverse=False)

    tf_j_list = []

    core_t_list=np.zeros(rs.m)
    for job_index in sorted_id:
        tf_j = tf_job(job_index, job_blocks_list[job_index], core_t_list, rs, e, core_allocation)
        tf_j_list.append(tf_j)
    #print(tf_j_list) #job????????????
    return e, tf_j_list, core, core_t_list, core_allocation, max(tf_j_list)


if __name__ == "__main__":
    rs = ResourceScheduler(taskType=1, caseID=2)
    X = np.zeros((rs.m, rs.max_k, rs.numJob))

    # X for case 1
    X[0][0][0] = 1
    X[0][0][2] = 2
    X[1][1][0] = 1
    X[1][1][2] = 2
    X[2][2][0] = 1
    X[2][2][2] = 2
    X[3][0][1] = 1
    X[3][1][1] = 2
    X[3][3][2] = 3

    # # X for case 2
    # X[0][0][0] = 1
    # X[0][2][0] = 2
    # X[1][1][0] = 1
    # X[2][0][1] = 1
    # X[2][1][1] = 2
    # X[2][2][3] = 3
    # X[3][2][1] = 1
    # X[3][0][3] = 2
    # X[4][0][2] = 1
    # X[4][3][3] = 2
    # X[5][1][2] = 1
    # X[5][1][3] = 2
    e, tf_j_list, core, core_t_list, core_allocation, obj = maxtf_job(X, rs)
    rs.outputSolutionFromBlock(e,tf_j_list, core, X, obj)
    rs.outputSolutionFromCore(core_t_list, core_allocation)

    print(obj)
