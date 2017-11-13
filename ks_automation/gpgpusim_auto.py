import os, shutil, subprocess, sys, time

#if os.name == 'posix' and sys.version_info[0] < 3:
#    import subprocess32 as subprocess
#else:
import subprocess

##bmDirRef = ["bc","color","color","fw","mis","pagerank","pagerank","sssp","sssp"]
##benchmarks = ["bc","color_max","color_maxmin","fw","mis","pagerank","pagerank_spmv","sssp","sssp_ell"]

##bmDirRef = ["color","color","fw","mis","pagerank","pagerank"]
##benchmarks = ["color_max","color_maxmin","fw","mis","pagerank","pagerank_spmv"]

bmDirRef = ["bc","sssp","sssp"]
benchmarks = ["bc","sssp","sssp_ell"]

bmDirRef2 = [r"cuda/backprop",r"cuda/lud",r"cuda/gaussian"]
benchmarks2 = ["backprop","lud","gaussian"]

fullBMDirRef = [r"cuda/backprop",r"cuda/lud","bc","mis"]
fullBMNames = ["backprop","lud","bc","mis"]
fullBMPathStarters = ["R","R","P","P"]

batchNumber = 3


def batchWorkloads(fullBMNames,fullBMDirRef,fullBMPathStarters,batchNumber):
    bmsOut = list()
    bmsDirsOut = list()
    bmsPathStartOut = list()
    while len(fullBMNames)>0:
        if len(fullBMNames)>=batchNumber:
            bmsOut.append(fullBMNames[0:(batchNumber)])
            fullBMNames = fullBMNames[batchNumber:]
            bmsDirsOut.append(fullBMDirRef[0:(batchNumber)])
            fullBMDirRef = fullBMDirRef[batchNumber:]
            bmsPathStartOut.append(fullBMPathStarters[0:(batchNumber)])
            fullBMPathStarters = fullBMPathStarters[batchNumber:]
        else:
            bmsOut.append(fullBMNames)
            fullBMNames = []
            bmsDirsOut.append(fullBMDirRef)
            fullBMDirRef = []
            bmsPathStartOut.append(fullBMPathStarters)
            fullBMPathStarters = []
    return [bmsOut,bmsDirsOut,bmsPathStartOut]

##file format
##
##NAME OF EXP
##normal file name = temp file name in preset directory (or full path)
##can do multiple of these lines
##all files are pre-made
##-----------------------
##next exp name
##...


#what this script needs to do:
#copy files over gpgpu-sim files
#remake gpgpu-sim (how to do this in linux world... does subprocess work?
#run each benchmark
#move results to results directory tree (results\BMNAME\jobname
def parseAutomationFile(inputFile):
    f = open(inputFile,'r')
    automationSteps = list()
    testNumDelimiter = "-----"
    automationSteps.append([])
    currIndex = 0
    for line in f:
        if line.find(testNumDelimiter) >= 0:
            currIndex += 1
            automationSteps.append([])
        elif len(line.split("%%%"))>1:
            automationSteps[currIndex].insert(0,line.replace("%","").replace("\n","").replace(" ",""))
        elif len(line.split("="))>=2:
            newFilePair = list()
            newFilePair.append(line.split("=")[0])
            newFilePair.append(line.split("=")[1].replace("\n","").replace(" ",""))
            automationSteps[currIndex].append(newFilePair)

    f.close()

    return automationSteps

def parseAutomationFileBM(inputFile):
    f = open(inputFile,'r')
    automationSteps = list()
    bms = list()
    bmDirs = list()
    testNumDelimiter = "-----"
    automationSteps.append([])
    currIndex = 0
    for line in f:
        if line.find(testNumDelimiter) >= 0:
            currIndex += 1
            automationSteps.append([])
        elif len(line.split("%%%"))>1:
            automationSteps[currIndex].insert(0,line.replace("%","").replace("\n","").replace(" ",""))
        elif len(line.split("="))>=2:
            newFilePair = list()
            newFilePair.append(line.split("=")[0])
            newFilePair.append(line.split("=")[1].replace("\n","").replace(" ",""))
            automationSteps[currIndex].append(newFilePair)
        elif line.find("bms")>=0:
            bms.append(line.split(":")[1].replace("\n","").split(","))
        elif line.find("bmDirs")>=0:
            bmDirs.append(line.split(":")[1].replace("\n","").split(","))

    f.close()

    return [automationSteps,bms, bmDirs]

def createOutputDirs(outputBaseFolderPath, outputBaseFolderName):
    for b2 in benchmarks2:
        if not os.path.exists(os.path.join(outputBaseFolderPath,b2)):
            os.mkdir(os.path.join(outputBaseFolderPath,b2))
            time.sleep(0.3)
            subprocess.call(["chmod", "777",os.path.join(outputBaseFolderPath,b2)])
        if os.path.exists(os.path.join(outputBaseFolderPath,b2,outputBaseFolderName)):
            print(outputBaseFolderName + " already exists! Abort!")
            raise
        newPath = os.path.join(outputBaseFolderPath,b2,outputBaseFolderName)
        os.mkdir(newPath)
        time.sleep(0.3)
        subprocess.call(["chmod", "777", newPath])
        
    for b in benchmarks:
        if not os.path.exists(os.path.join(outputBaseFolderPath,b)):
            os.mkdir(os.path.join(outputBaseFolderPath,b))
            time.sleep(0.3)
            subprocess.call(["chmod", "777",os.path.join(outputBaseFolderPath,b)])
        if os.path.exists(os.path.join(outputBaseFolderPath,b,outputBaseFolderName)):
            print(outputBaseFolderName + " already exists! Abort!")
            raise
        newPath = os.path.join(outputBaseFolderPath,b,outputBaseFolderName)
        os.mkdir(newPath)
        time.sleep(0.3)
        subprocess.call(["chmod", "777", newPath])

def createOutputDirsGen(myBMs, outputBaseFolderPath, outputBaseFolderName):
    for b in myBMs:
        if not os.path.exists(os.path.join(outputBaseFolderPath,b)):
            os.mkdir(os.path.join(outputBaseFolderPath,b))
            time.sleep(0.3)
            subprocess.call(["chmod", "777",os.path.join(outputBaseFolderPath,b)])
        if os.path.exists(os.path.join(outputBaseFolderPath,b,outputBaseFolderName)):
            print(outputBaseFolderName + " already exists! Abort!")
            raise
        newPath = os.path.join(outputBaseFolderPath,b,outputBaseFolderName)
        os.mkdir(newPath)
        time.sleep(0.3)
        subprocess.call(["chmod", "777", newPath])

def moveFilesForTest(automationSteps):
    for pair in automationSteps:
        dest = pair[0]
        source = pair[1]
        try:
            shutil.copy(source,dest)
        except:
            print("couldn't copy " + source + " to " + dest)
            raise

def remakeCode(baseCodeDir):
    #need to figure this out
    subprocess.call("make",cwd=baseCodeDir)
    #time.sleep(60)

def remakeCodeDocker(baseCodeDir,scriptSubPath):
    #subprocess.call(["source", "setup_environment"],cwd=baseCodeDir)
    #subprocess.call("make",cwd=baseCodeDir)
##    subprocess.call(["bash", "make.bash"],cwd=baseCodeDir)
    print(dockerBaseMake +baseCodeDir+scriptSubPath)
    subprocess.call((dockerBaseMake + baseCodeDir+scriptSubPath).split(" "))

def runTest(benchmarkToRun, baseBenchmarksDirectory, benchmarkToRunDir):
    print(os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))
    subprocess.Popen(["bash","run.bash"], cwd=os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))

def runTestFinal(benchmarkToRun, baseBenchmarksDirectory, benchmarkToRunDir):
    print(os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))
    subprocess.call(["bash","run.bash"], cwd=os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))

def runTestDockerRodinia(benchmarkToRun, baseBenchmarksDirectory, benchmarkToRunDir):
    print(os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))
    dockerFullCall = dockerBase + r"gpu-rodinia/" + benchmarkToRunDir + r"/run_" + benchmarkToRun + r"/run.bash"
    print(dockerFullCall)
    cmdArray = dockerFullCall.split(" ")
    subprocess.Popen(cmdArray, cwd=os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))

def runTestDockerRodiniaFinal(benchmarkToRun, baseBenchmarksDirectory, benchmarkToRunDir):
    print(os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))
    dockerFullCall = dockerBase + r"gpu-rodinia/" + benchmarkToRunDir + r"/run_" + benchmarkToRun + r"/run.bash"
    print(dockerFullCall)
    cmdArray = dockerFullCall.split(" ")
    subprocess.call(cmdArray, cwd=os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))

def runTestDocker(benchmarkToRun, baseBenchmarksDirectory, benchmarkToRunDir):
    print(os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))
    dockerFullCall = dockerBase + r"pannotia/" + benchmarkToRunDir + r"/run_" + benchmarkToRun + r"/run.bash"
    print(dockerFullCall)
    cmdArray = dockerFullCall.split(" ")
    subprocess.Popen(cmdArray, cwd=os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))

def runTestDockerFinal(benchmarkToRun, baseBenchmarksDirectory, benchmarkToRunDir):
    print(os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))
    dockerFullCall = dockerBase + r"pannotia/" + benchmarkToRunDir + r"/run_" + benchmarkToRun + r"/run.bash"
    print(dockerFullCall)
    cmdArray = dockerFullCall.split(" ")
    subprocess.call(cmdArray, cwd=os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun))

def copyResults(baseBenchmarksDirectory, benchmarkToRun,benchmarkToRunDir, outputBaseFolderPath, outputBaseFolderName):
    try:
        shutil.copy(os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun,"output"),os.path.join(outputBaseFolderPath,benchmarkToRun,outputBaseFolderName,"output"))
        shutil.copy(os.path.join(baseBenchmarksDirectory,benchmarkToRunDir,"run_"+benchmarkToRun,"result.out"),os.path.join(outputBaseFolderPath,benchmarkToRun,outputBaseFolderName,"result.out"))
    except:
        print("copying failed (or result.out didn't exist) for " + outputBaseFolderName + " on bm:" + benchmarkToRun)

def checkTouchFiles(benchmarks,bmDirRef,bmPathStart):
    for b in range(len(benchmarks)):
        currBM = benchmarks[-1]
        currBMDirRef = bmDirRef[-1]
        currBMPath = bmPathStart[-1]
        if currBMPath.find("R") >=0:
            baseBenchPath = baseBenchmarksDirectory2
        else:
            baseBenchPath = baseBenchmarksDirectory
        boolStatus = os.path.exists(os.path.join(baseBenchPath,currBMDirRef,"run_"+currBM,"status.txt"))
        if boolStatus == False:
            return False
    return True

def rmTouchFiles(benchmarks,bmDirRef,bmPathStart):
    for b in range(len(benchmarks)):
        currBM = benchmarks[-1]
        currBMDirRef = bmDirRef[-1]
        currBMPath = bmPathStart[-1]
        if currBMPath.find("R") >=0:
            baseBenchPath = baseBenchmarksDirectory2
        else:
            baseBenchPath = baseBenchmarksDirectory
        os.remove(os.path.join(baseBenchPath,currBMDirRef,"run_"+currBM,"status.txt"))


outputBaseFolderPath = r"/home/kkstraube/gpgpu-sim/ks_automation/outputs"
inputFile = r"/home/kkstraube/gpgpu-sim/ks_automation/capp_per_bm.txt"
baseBenchmarksDirectory = r"/home/kkstraube/gpgpu-sim/pannotia"
baseBenchmarksDirectory2 = r"/home/kkstraube/gpgpu-sim/gpu-rodinia"
dockerBase = r"docker run -v /home/kkstraube/gpgpu-sim:/home/kkstraube/gpgpu-sim -it powerjg/gpgpu-sim-build /home/kkstraube/gpgpu-sim/"
dockerBaseMake = r"docker run -v /home/kkstraube/gpgpu-sim:/home/kkstraube/gpgpu-sim -it powerjg/gpgpu-sim-build "

def runWLBatchAutomation():
    autoSteps = parseAutomationFile(inputFile)
    for job in autoSteps:
        jobName = job[0]
        print(job)
        allStepsForThisJob = job[1:]
        createOutputDirsGen(fullBMNames,outputBaseFolderPath, jobName)
        moveFilesForTest(allStepsForThisJob)
        time.sleep(0.3)
        remakeCodeDocker(baseBenchmarksDirectory+r"/pagerank/run_pagerank/","run2.bash")
        [wlBatches,wlBatchesDir,wlBatchesPath] = batchWorkloads(fullBMNames,fullBMDirRef,fullBMPathStarters,batchNumber)
        for b in range(len(wlBatches)):
            benchmarks = wlBatches[b]
            bmDirRef = wlBatchesDir[b]
            bmPathStart = wlBatchesPath[b]
            for i in range(len(benchmarks[0:-1])):
                currBM = benchmarks[i]
                currBMDirRef = bmDirRef[i]
                currBMPath = bmPathStart[i]
                if currBMPath.find("R") >=0:
                    baseBenchPath = baseBenchmarksDirectory2
                else:
                    baseBenchPath = baseBenchmarksDirectory
                print(currBM)
                #time.sleep(10)
                runTestDocker(currBM, baseBenchDir,currBMDirRef)
            currBM = benchmarks[-1]
            currBMDirRef = bmDirRef[-1]
            currBMPath = bmPathStart[-1]
            print(currBM + " FINAL!")
            if currBMPath.find("R") >=0:
                baseBenchPath = baseBenchmarksDirectory2
            else:
                baseBenchPath = baseBenchmarksDirectory
            runTestDockerFinal(currBM, baseBenchPath,currBMDirRef)

            while checkTouchFiles(benchmarks,bmDirRef,bmPathStart) != True:
                time.sleep(3600)
            rmTouchFiles(benchmarks,bmDirRef,bmPathStart)
            for i in range(len(benchmarks)):
                currBM = benchmarks[i]
                currBMDirRef = bmDirRef[i]
                currBMPath = bmPathStart[-1]
                if currBMPath.find("R") >=0:
                    baseBenchPath = baseBenchmarksDirectory2
                else:
                    baseBenchPath = baseBenchmarksDirectory
                copyResults(baseBenchPath, currBM,currBMDirRef, outputBaseFolderPath, jobName)

##if False:
##    autoSteps = parseAutomationFile(inputFile)
##
##    for job in autoSteps:
##        jobName = job[0]
##        print(job)
##        allStepsForThisJob = job[1:]
##        createOutputDirs(outputBaseFolderPath, jobName)
##        moveFilesForTest(allStepsForThisJob)
##        time.sleep(0.3)
##        remakeCodeDocker(baseBenchmarksDirectory+r"/pagerank/run_pagerank/","run2.bash")
##        for i in range(len(benchmarks[0:-1])):
##            currBM = benchmarks[i]
##            currBMDirRef = bmDirRef[i]
##            print(currBM)
##            #time.sleep(10)
##            runTestDocker(currBM, baseBenchmarksDirectory,currBMDirRef)
##        currBM = benchmarks[-1]
##        currBMDirRef = bmDirRef[-1]
##        print(currBM + " FINAL!")
##        runTestDockerFinal(currBM, baseBenchmarksDirectory,currBMDirRef)
##        for i in range(len(benchmarks)):
##            currBM = benchmarks[i]
##            currBMDirRef = bmDirRef[i]
##            copyResults(baseBenchmarksDirectory, currBM,currBMDirRef, outputBaseFolderPath, jobName)
##        #break
##    ##remakeCode(ospath.join(r"/home/kkstraube/gpgpu-sim/pannotia",bmDirRef)
##else:
####    inputFile = r"E:\research_store\gpu\ks_automation\testJob1BM.txt"
##    autoStepsAll = parseAutomationFileBM(inputFile)
##    autoSteps = autoStepsAll[0]
##    benchmarksAll = autoStepsAll[1]
##    bmDirRefAll = autoStepsAll[2]
##    benchmarks2 = []
####    print(autoSteps)
####    print(benchmarksAll)
####    print(bmDirRefAll)
##    for jobIndex in range(len(autoSteps)):
##        job = autoSteps[jobIndex]
##        benchmarks = benchmarksAll[jobIndex]
##        bmDirRef = bmDirRefAll[jobIndex]
##        jobName = job[0]
##        print(job)
##        allStepsForThisJob = job[1:]
##        createOutputDirs(outputBaseFolderPath, jobName)
##        moveFilesForTest(allStepsForThisJob)
##        time.sleep(0.3)
##    ##    remakeCode(r"/home/kkstraube/gpgpu-sim")
##        remakeCodeDocker(baseBenchmarksDirectory+r"/pagerank/run_pagerank/","run2.bash")
##    #r"/home/kkstraube/gpgpu-sim","make.bash")
##        #break
##        for i in range(len(benchmarks[0:-1])):
##            currBM = benchmarks[i]
##            currBMDirRef = bmDirRef[i]
##            print(currBM)
##            #time.sleep(10)
##            runTestDocker(currBM, baseBenchmarksDirectory,currBMDirRef)
##        currBM = benchmarks[-1]
##        currBMDirRef = bmDirRef[-1]
##        print(currBM + " FINAL!")
##        runTestDockerFinal(currBM, baseBenchmarksDirectory,currBMDirRef)
##        for i in range(len(benchmarks)):
##            currBM = benchmarks[i]
##            currBMDirRef = bmDirRef[i]
##            copyResults(baseBenchmarksDirectory, currBM,currBMDirRef, outputBaseFolderPath, jobName)
