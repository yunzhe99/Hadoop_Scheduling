from env import ResourceScheduler
from sample_fun import sol_init, sample
from tools import maxtf_job
import numpy as np
from SA import SAoptimizer
import joblib


rs = ResourceScheduler(taskType=1, caseID=2)

b=rs.max_k
block_size=rs.dataSize
s_list=rs.Sc
if rs.taskType==2:
    s_t=rs.St
alpha=rs.alpha
block_location=rs.location
core_location=rs.core_location

job_schedule, job_order = sol_init(rs.numJob, len(rs.core_location), rs.dataSize, max(rs.jobBlock))

def init_f():
    schedule, order, x=sample(job_schedule, job_order, len(rs.core_location), rs.numJob, max(rs.jobBlock), 1)
    return x

def randf(x_old, job_schedule=job_schedule, job_order=job_order):
    schedule, order, x_new=sample(job_schedule, job_order, rs.hostCore[0], rs.numJob, max(rs.jobBlock), 1)
    job_schedule, job_order = schedule, order
    return x_new


if __name__ == '__main__':

    sa = SAoptimizer()

    #print(maxtf_job(init_f()))
    
    # b=rs.max_k
    # block_size=rs.dataSize
    # s_list=rs.Sc
    # if rs.taskType==2:
    #     s_t=rs.St
    # alpha=rs.alpha
    # block_location=rs.location
    # core_location=rs.core_location

    x_best, y_best = sa.optimize(f = maxtf_job, ybound=(0, np.inf), initf=init_f, randf=randf,
        t=1000, alpha=0.98, stop=0.01, iterPerT=10, l=1)
    print(y_best)
    print(x_best)
    # joblib.dump((x_best, y_best))
    # x, y = sa.optimize(f = maxtf_job, ybound=(0, np.inf), initf=init_f, randf=randf,
    #         t=1000, alpha=0.98, stop=0.01, iterPerT=1, l=1)
    # print(y)
    for i in range(1):
        # job_schedule, job_order = sol_init(rs.numJob, len(rs.core_location), rs.dataSize, max(rs.jobBlock))
        x, y = sa.optimize(f = maxtf_job, ybound=(0, np.inf), initf=init_f, randf=randf,
            t=1000, alpha=0.98, stop=0.01, iterPerT=10, l=1)
        print(y)
        if y < y_best:
            y_best=y
            x_best=x

    # print()
    # print(y_best)
    # print(x_best)

