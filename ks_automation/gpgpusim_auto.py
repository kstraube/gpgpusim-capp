import os, shutil, subprocess, sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

bmDirRef = ["color","fw","mis","pagerank","sssp"]
benchmarks = ["color_max","fw","mis","pagerank","sssp"]

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
            os.makedirs(os.path.join(outputBaseFolderPath,b),777)
        if os.path.exists(os.path.join(outputBaseFolderPath,b,outputBaseFolderName)):
            print(outputBaseFolderName + " already exists! Abort!")
            raise
        newPath = os.path.join(outputBaseFolderPath,b,outputBaseFolderName)
        os.makedirs(newPath,777)

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
    subprocess.Popen("make",cwd=baseCodeDir)

def runTest(benchmarkToRun, baseBenchmarksDirectory):
    subprocess.Popen(".\run.bash", cwd=os.path.join(baseBenchmarksDirectory,benchmarkToRun,"run_"+benchmarkToRun))

def copyResults(baseBenchmarksDirectory, benchmark, outputBaseFolderPath, outputBaseFolderName):
    try:
        shutil.copy(os.path.join(baseBenchmarksDirectory,benchmarkToRun,"run_"+benchmarkToRun,"output"),os.path.join(outputBaseFolderPath,benchmark,outputBaseFolderName,"output"))
        shutil.copy(os.path.join(baseBenchmarksDirectory,benchmarkToRun,"run_"+benchmarkToRun,"result.out"),os.path.join(outputBaseFolderPath,benchmark,outputBaseFolderName,"result.out"))
    except:
        print("copying failed (or result.out didn't exist) for " + outputBaseFolderName + " on bm:" + benchmark)

inputFile = r"/home/kkstraube/gpgpu-sim/ks_automation/testJob1.txt"

parseAutomationFile(inputFile)

currBM = benchmarks[0]
currBMDirRef = bmDirRef[0]
remakeCode(r"/home/kkstraube/gpgpu-sim")
##remakeCode(os.path.join(r"/home/kkstraube/gpgpu-sim/pannotia",bmDirRef)
        
