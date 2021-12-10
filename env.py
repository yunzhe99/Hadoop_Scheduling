from sko.SA import SA
import matplotlib.pyplot as plt
import pandas as pd
import numpy as  np
import util

class ResourceScheduler(object):
    """
    taskType: 1~2
    caseID: 1
    numJob: 0~n-1
    numHost: 0~
    St: speed of Transimision
	alpha: g(e)=1-alpha(e-1) alpha>0, e is the number of cores allocated to a single job
    hostCore: the number of cores for each host
    jobBlock: the number of blocks for each job
    max_k
    Sc: speed of calculation for each job
    dataSize: job-> block number-> block size
    location: job-> block number-> block location (host number)
    jobFinishTime: the finish time of each job 
    jobCore: the number of cores allocated to each job

    runLoc: block perspective: job number->block number->(hostID, coreID,rank), rank=1 means that block is the first task running on that core of that host
    hostCoreTask: core perspective: host->core->task-> <job,block,startTime,endTime>
    
    hostCoreFinishTime: host->core->finishTime
    """
    def __init__(self, taskType=1, caseID=1):
        super(ResourceScheduler, self).__init__()
        self.taskType = taskType
        self.caseID = caseID
        self.data = []
        data_path = "./input/task" + str(taskType) + "_case" + str(caseID)+".txt"
        with open(data_path, "r") as f:
            for line in f:
                for i in line.split():
                    if i.isdigit():
                        self.data.append(int(i))
                    elif util.is_number(i):
                        self.data.append(float(i))
        idata = iter(self.data)

        self.numJob = next(idata)
        self.numHost = next(idata)
        self.alpha = float(next(idata))
        if taskType == 2:
            self.St = next(idata)

        self.hostCore = np.empty(self.numHost, dtype=int)
        for i  in range(self.numHost):
            self.hostCore[i] = next(idata)
        
        self.core_location=[] # 意义同tools
        for i in range(self.numHost):
            self.core_location+=[i]*self.hostCore[i]

        self.jobBlock = np.empty(self.numJob, dtype=int)
        for i in range(self.numJob):
            self.jobBlock[i] = next(idata)

        self.max_k = max(self.jobBlock)
        
        self.Sc = np.empty(self.numJob, dtype=int)
        for i in range(self.numJob):
            self.Sc[i] = next(idata)
        
        self.dataSize = []
        for i in range(self.numJob):
            self.dataSize.append(np.empty(self.jobBlock[i], dtype=int))
            for j in range(int(self.jobBlock[i])):
                self.dataSize[i][j] = next(idata)
        
        self.location = []
        for i in range(self.numJob):
            self.location.append(np.empty(self.jobBlock[i], dtype=int))
            for j in range(int(self.jobBlock[i])):
                self.location[i][j] = next(idata)

        self.jobFinishTime = np.empty(self.numJob, dtype=int)
        self.jobCore = np.empty(self.numJob, dtype=int)

        self.runLoc = []

        self.hostCoreTask = []

        self.hostCoreFinishTime = []
        for i in range(self.numHost):
            self.hostCoreFinishTime.append(np.empty(self.hostCore[i], dtype=int))

    def outputSolutionFromBlock():
        pass
    def outputSolutionFromCore():
        pass

    def g(self, e):
        return 1 - self.alpha * (e - 1)

def demo_func(x):
    x1, x2, x3 = x
    return x1 ** 2 + (x2 - 0.05) ** 2 + x3 ** 2


if __name__ == '__main__':
    rs = ResourceScheduler()
    e = 3
    print(rs.max_k)
    sa = SA(func=demo_func, x0=[1, 1, 1], T_max=1, T_min=1e-9, L=300, max_stay_counter=150)
    best_x, best_y = sa.run()
    print('best_x:', best_x, 'best_y', best_y)
    plt.plot(pd.DataFrame(sa.best_y_history).cummin(axis=0))
    plt.show()

