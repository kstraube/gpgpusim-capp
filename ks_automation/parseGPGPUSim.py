import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import numpy
import os

def parsePagerankStats(filename, nc):
    allPows = list()
    allETs = list()
    allFreqs = list()
    allStats = {}
    allStats['total power'] = list()
    allStats['PID error'] = list()
    allStats['voltage'] = list()
    allStats['gpu_sim_cycle'] = list()
    lineList = []
    iterVal = 0
    for n in range(nc):
        allPows.append([])
        allETs.append([])
        allFreqs.append([])
    f = open(filename)
    for line in f:
        if line.find("for core") >= 0:
            corePow = line.split("for core")[0].split("=")[1]
            coreNum = line.split("for core")[1].replace("\n","")
            allPows[int(coreNum)].append(corePow)
            allETs[int(coreNum)].append(execTime)
            allFreqs[int(coreNum)].append(freq)
            for i in range(iterVal):
                if list(allStats.keys()).count(lineList[2*i]) == 0:
                    allStats[lineList[2*i]] = list()
                    for n in range(nc):
                        allStats[lineList[2*i]].append([])
                allStats[lineList[2*i]][int(coreNum)].append(lineList[2*i+1])
        elif line.find("executionTime")>=0:
            execTime = line.split(":")[1].replace("\n","")
        elif line.find("FREQ:")>=0:
            freq = float(line.split(":")[1].replace(" ","").replace("\n",""))
        elif line.find("tot_inst") >= 0:
            lineList = line.replace("\n","").split(":")
            iterVal = int(len(lineList)/2)
        elif line.find("tot pow:") >=0:
            allStats['total power'].append(float(line.split(":")[1].replace(" ","").replace("\n","")))
        elif line.find("gpu_tot_sim_cycle")>=0:
            allStats['gpu_tot_sim_cycle'] = line.split("=")[1].replace(" ","").replace("\n","")
        elif line.find("kernel + memcpy time")>=0:
            print(line)
            if line.count("=")>0:
                allStats['gpu_sim_cycle'].append(line.split("=")[1].replace(" ","").replace("\n",""))
            else:
                allStats['gpu_sim_cycle'].append(line.replace("kernel + memcpy time","").replace(" ","").replace("\n",""))
        elif line.find("voltage:")>=0:
            allStats['voltage'].append(line.split(":")[1].replace(" ","").replace("\n",""))
        elif line.find("PID error:")>=0:
            allStats['PID error'].append(line.split(":")[1].replace(" ","").replace("\n",""))
##            print(iterVal)
##            print(lineList)
##            return lineList
             

    f.close()
    return [allPows,allFreqs,allETs, allStats]

def plotStat(metric, coreNums):
    k=0
    styleType = ['r--','b--','g--','r-','b-','g-','r:','b:','g:']
    t = range(len(allStats[metric][coreNums[0]]))
    for i in coreNums:
        plt.plot(t,allStats[metric][i],styleType[k])
        k+= 1
    plt.show()

def plotPower():
    t = range(len(allStats['total power']))
    plt.plot(t,allStats['total power'])
    plt.show()

def plotVoltage():
    t = range(len(allStats['voltage']))
    plt.plot(t,allStats['voltage'])
    plt.show()

def plotPIDError():
    t = range(len(allStats['PID error']))
    plt.plot(t,allStats['PID error'])
    plt.show()

def movingaverage(interval, window_size):
    window= numpy.ones(int(window_size))/float(window_size)
    return numpy.convolve(interval, window, 'same')

plt.ion()
root = tk.Tk()
root.withdraw()

def parseFile():
    file_path = filedialog.askopenfilename(initialdir=r"E:\research_store\gpu")

    [allPows,allFreqs,allETs, allStats] = parsePagerankStats(file_path,16)
        #r"E:\research_store\gpu\CAPP2level\output",16)
    allStats['power'] = allPows
    allStats['execTime'] = allETs
    allStats['freq'] = allFreqs
    ##totpower = list(map(float,allStats['total power']))
    try:
        print("results = " + str(allStats['gpu_tot_sim_cycle']))# + " full = " + allStats['results_full'])
    except:
        print("printing results failed")

    return allStats


TDPspec = 59.0

def getAllResults(folderName):
    for f in os.listdir(folderName):
        if not (os.path.isdir(os.path.join(folderName,f))):
            continue
        elif f.find("archive")>=0:
            continue
        else:
            resFile = os.path.join(folderName,f,"output")
            [allPows,allFreqs,allETs, allStats] = parsePagerankStats(resFile,16)
            totpow = allStats['total power']
            totpow_mv100 = movingaverage(totpow,100)
            powutil = [p/TDPspec for p in totpow]
            powutil_mv100 = movingaverage(powutil,100)
            print("folder name= " + f)
            print("total power = " + str(sum(totpow)/len(totpow)))
            print("total power mv 100 = " + str(sum(totpow_mv100)/len(totpow_mv100)))
            print("max power = " + str(max(totpow)))
            print("max power mv 100 = " + str(max(totpow_mv100)))
            print("power utilization average= " + str(sum(powutil)/len(powutil)))
            print("power utilization mv 100 average= " + str(sum(powutil_mv100)/len(powutil_mv100)))
            print("total cycles = " + str(allStats['gpu_tot_sim_cycle']))

def allBMResToFile(baseFolder,fileOutName=r"E:\research_store\gpu\reportOut.csv"):
    headers = ["Benchmark","Job Name","Total Cycles","Total Power","Total Power MV100","Max Power", "Max Power MV100","Power Utilization","Power Utilization MV100"
               ,"STDev Total Power","STDev Total Power MV100","Average Frequency"]
    fOut = open(fileOutName,'w')
    fOut.write(",".join(headers)+"\n")
    for bmDir in os.listdir(baseFolder):
        currBMDir = os.path.join(baseFolder,bmDir)
        if currBMDir.find("dataMerge") >=0:
            continue
        for jobDir in os.listdir(currBMDir):
            resFile = os.path.join(currBMDir,jobDir,"output")
            print(os.path.join(currBMDir,jobDir))
            [allPows,allFreqs,allETs, allStats] = parsePagerankStats(resFile,16)
            totpow = allStats['total power']
            totpow_mv100 = movingaverage(totpow,100)
            powutil = [p/TDPspec for p in totpow]
            powutil_mv100 = movingaverage(powutil,100)
            print(str(sum(allFreqs[0])/len(allFreqs[0])))
            fOut.write(",".join([bmDir,jobDir,str(allStats['gpu_tot_sim_cycle']),str(sum(totpow)/len(totpow)),str(sum(totpow_mv100)/len(totpow_mv100)),
                                 str(max(totpow)),str(max(totpow_mv100)),str(sum(powutil)/len(powutil)),str(sum(powutil_mv100)/len(powutil_mv100)),
                                 str(numpy.std(totpow)),str(numpy.std(totpow_mv100)),str(sum(allFreqs[0])/len(allFreqs[0])) ]) + "\n")

    fOut.close()
            
    return
