import os, shutil, subprocess, sys, time

#if os.name == 'posix' and sys.version_info[0] < 3:
#    import subprocess32 as subprocess
#else:
import subprocess

##bmDirRef = ["bc","color","color","fw","mis","pagerank","pagerank","sssp","sssp"]
##benchmarks = ["bc","color_max","color_maxmin","fw","mis","pagerank","pagerank_spmv","sssp","sssp_ell"]

bmDirRef = ["color","color","fw","mis","pagerank","pagerank"]
benchmarks = ["color_max","color_maxmin","fw","mis","pagerank","pagerank_spmv"]

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

def createOutputDirs(outputBaseFolderPath, outputBaseFolderName):
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


outputBaseFolderPath = r"/home/kkstraube/gpgpu-sim/ks_automation/outputs"
inputFile = r"/home/kkstraube/gpgpu-sim/ks_automation/job_expandedVF_capp.txt"
baseBenchmarksDirectory = r"/home/kkstraube/gpgpu-sim/pannotia"
dockerBase = r"docker run -v /home/kkstraube/gpgpu-sim:/home/kkstraube/gpgpu-sim -it powerjg/gpgpu-sim-build /home/kkstraube/gpgpu-sim/"
dockerBaseMake = r"docker run -v /home/kkstraube/gpgpu-sim:/home/kkstraube/gpgpu-sim -it powerjg/gpgpu-sim-build "

autoSteps = parseAutomationFile(inputFile)

for job in autoSteps:
    jobName = job[0]
    print(job)
    allStepsForThisJob = job[1:]
    createOutputDirs(outputBaseFolderPath, jobName)
    moveFilesForTest(allStepsForThisJob)
    time.sleep(0.3)
##    remakeCode(r"/home/kkstraube/gpgpu-sim")
    remakeCodeDocker(baseBenchmarksDirectory+r"/pagerank/run_pagerank/","run2.bash")
#r"/home/kkstraube/gpgpu-sim","make.bash")
    #break
    for i in range(len(benchmarks[0:-1])):
        currBM = benchmarks[i]
        currBMDirRef = bmDirRef[i]
        print(currBM)
        #time.sleep(10)
        runTestDocker(currBM, baseBenchmarksDirectory,currBMDirRef)
    currBM = benchmarks[-1]
    currBMDirRef = bmDirRef[-1]
    print(currBM + " FINAL!")
    runTestDockerFinal(currBM, baseBenchmarksDirectory,currBMDirRef)
    for i in range(len(benchmarks)):
        currBM = benchmarks[i]
        currBMDirRef = bmDirRef[i]
        copyResults(baseBenchmarksDirectory, currBM,currBMDirRef, outputBaseFolderPath, jobName)
    #break
##remakeCode(ospath.join(r"/home/kkstraube/gpgpu-sim/pannotia",bmDirRef)
        
