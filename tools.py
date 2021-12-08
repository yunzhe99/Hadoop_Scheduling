import numpy as np


c = 4  # number of cores
b = 4  # the max number of blocks
n = 3  # number of jobs

# job * block
block_size = [[10, 20, 16],
                [9, 16],
                [10, 6, 20, 15]]
# 1 * core
s_list = [5, 5, 5, 5]
alpha = 0.03
# the available core time for now
core_t_list = np.zeros(c)


def tf_core(job_index, core_blocks, core_used, t):
    # time of finish for a core
    size_core = 0
    for core_block in core_blocks:
        size_block = block_size[core_block[2]][core_block[1]]
        size_core += size_block
    tp = size_core / (s_list[job_index] * (1 - 0.03 * (len(core_used) - 1)))
    tf = t + tp
    core_t_list[core_blocks[0][0]] = tf
    return tf


def tf_job(X, job_index, job_blocks):
    # time of finish for a job
    core_used = set()
    for job_block in job_blocks:
        core_used.add(job_block[0])
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
        tf = tf_core(X, job_index, core_blocks, core_used, t)
        if tf_j < tf:
            tf_j = tf
    return tf_j


def maxtf_job(X):
    # job order sort
    job_p_list = []
    job_blocks_list = []
    for job_index in range(X.shape[2]):
        job_blocks = []
        block_p_list = []
        for core_index in range(X.shape[0]):
            for block_index in range(X.shape[1]):
                if X[core_index][block_index][job_index] != 0:
                    job_blocks.append([core_index, block_index, job_index])
                    block_p_list.append(X[core_index][block_index][job_index])
        job_p = np.mean(block_p_list)
        job_p_list.append(job_p)
        job_blocks_list.append(job_blocks)
    sorted_id = sorted(range(len(job_p_list)), key=lambda k: job_p_list[k], reverse=False)

    tf_j_list = []

    for job_index in sorted_id:
        tf_j = tf_job(X, job_index, job_blocks_list[job_index])
        tf_j_list.append(tf_j)
    return max(tf_j_list)


if __name__ == "__main__":
    X = np.zeros((c, b, n))
    X[0][0][0] = 1
    X[0][0][2] = 2
    X[1][1][0] = 1
    X[1][1][2] = 2
    X[2][2][0] = 1
    X[2][2][2] = 2
    X[3][0][1] = 1
    X[3][1][1] = 2
    X[3][3][2] = 3
    obj = maxtf_job(X)
    print(obj)
