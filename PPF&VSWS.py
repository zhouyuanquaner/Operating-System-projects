Requirement:
Realize PFF and VSWS algorithms and compare them. Commit the conclusion in commit.
===============================

import random
import linecache

pageOccupy = 10000
pageUse = 100
residentSet = ''
residentSet = map(int, residentSet)
useBitSet = ''
useBitSet = map(int, useBitSet)
F = 25
M = 15
L = 30
Q = 20
#-------------------------------------------------------------------------------------------------------
#PFF
# At first, I change several F value to decide the optimal one. if F is very small, like 1, the size of the resident set is between [0,3], very small, and the pageFault
#number is near to the page occupy number. If the F is too large, the set size would be big but the total number of page fault is small. After many tries, I use F = 25 
#since it has much less page fault(675) and the size of resident set is not too large.
#VSWS############
#At first because the process just use pageUse = 100 pages, it's no meaning to let L>=100 or Q>=100. Then I tried many different value of these three parameters.
#Since the 'process' is not a real process, every time the timer larger than L, it will drop all the pages and as a result, so the total number of page fault is very large.
# If the M is very small, clear or not is much depends on the number of page faults, i.e., the value of Q. If the M is very large, it is more like PFF and we always 
#increasing the size of resident set, wasting the CPU resources.
#If L is large, the maximum duration of interval is long. It means we suppose current process need long time to run. And if L is small, means that
#we suppose that the process will end in a short period of time. On the other hand, the larger L, the larger minimum size of resident set and smaller amount of page fault. 
# The Q control the max number of page fault during the time between M and L. It monitors if it is a 'new process' or not and also control the size of resident set from
# be too large. The larger Q, the relative larger max size of resident set and less total number of page fault.


#COMPARE
#When it starts a new process, it is much better for using VSWS, since it can judge the situation automatically and drop the old process by itself, which really save the 
# space and has higher efficiency. It can always keep a smaller size of resident set, which benefit the CPU. But for PFF, it always use longer time to drop those useless
#frames. It is not good at manage the situation when new process runs.

#In this project, after choose a proper value of parameters. I found that both of the max size and the average size of the resident set size is much better in VSWS. 
#And the total number of page fault of VSWS is larger than PFF since it clean the resident size more frequent than PFF.

#-------------------------------------------------------------------------------------------------------

# in my homework, I suppose that every page needs equal time to run. In other words, we use unit of time to run every page.


def createFile():
	# Choose a file to simulate the process, I select a txt file in my system
	# The very first line represents the number of page the process need while running
	# The subsequent line represents the page reference the process need currently
	f = open("/Users/Tammy/Documents/yuan.txt", 'w')
	f.write(str(pageOccupy))
	f.write('\n')
	temp = ''
	for i in range(pageOccupy):
		temp += str(random.randint(1,pageUse)) + "\n"
	f.write(temp[:-1])
	f.close()

def initialize():
	#f = open("/Users/Tammy/Documents/yuan.txt", 'r')
	f = open("/Users/Tammy/Documents/yuan.txt",'r')
	content = f.read()
	f.close()
	content = content.split('\n')
	return content

def getUsingPage(i,content):
	pageUsing = content[int(i)]
	pageUsing = int(pageUsing)
	return pageUsing

def cleanResident(residentSet,useBitSet):
	k = len(useBitSet) - 1
	while(k>=0):# throw out those pages whose use bit is 0
		if useBitSet[k] == 0:
			useBitSet.pop(k)
			residentSet.pop(k)
		k -= 1
	# reset the use bit on the remaining pages of the process to 0.
	for j in range(0, len(useBitSet)):
		if useBitSet[j] == 1:
			useBitSet[j] =0


def pff(residentSet, useBitSet):
	# simulate that we now run the process
	lastFault = 0
	thisFault = 0
	content = initialize()
	maxPFF = 0
	minPFF = pageOccupy
	totalPageFault = 0
	for i in range(1, pageOccupy+ 1):
		pageUsing = getUsingPage(i,content)
		if pageUsing not in residentSet:
			totalPageFault += 1
			thisFault = i
			faultTimeInterval = thisFault - lastFault
			if faultTimeInterval < F :
				#the page is added to the resident set of the process.
				residentSet.append(pageUsing)
				useBitSet.append(1) 
			if faultTimeInterval >= F :
				cleanResident(residentSet,useBitSet)
				minPFF = min(minPFF, len(residentSet))
				residentSet.append(pageUsing)
				useBitSet.append(1) 
			lastFault = thisFault
		elif pageUsing in residentSet:
			pageUsingIndex = residentSet.index(pageUsing)
			useBitSet[pageUsingIndex] = 1
		maxPFF = max(maxPFF, len(residentSet))
	print 'PFF'
	print "min:", minPFF
	print "max:", maxPFF
	print 'total number of page fault is ', totalPageFault



def vsws(residentSet, useBitSet):
	content = initialize()
	i = 1 #Since the first line is the number of pages the process occupies, we start from the second number
	#run the whole process
	maxVSWS = 0
	minVSWS = pageOccupy
	totalPageFault = 0
	while (i <= pageOccupy ):
		#start a sampling interval
		pageFaultNum = 0 # initialize the counter of the fault number
		timer = 0
		cleanResident(residentSet,useBitSet)
		minVSWS = min(minVSWS, len(residentSet))
		while (timer < L and i<= pageOccupy ):				
			timer += 1
			pageUsing = getUsingPage(i, content)
			maxVSWS = max(maxVSWS, len(residentSet))
			# the pages that have been referenced during the interval will have their use bit set
			if pageUsing in residentSet:
				pageUsingIndex = residentSet.index(pageUsing)
				useBitSet[pageUsingIndex] = 1
			#any faulted pages are added to the resident set
			elif pageUsing not in residentSet:
				pageFaultNum += 1
				totalPageFault += 1
				#if M time has elapsed and the page fault number is larger than Q, suspend and scan
				if pageFaultNum >= Q:
					if timer >=M:
						timer = 0
						pageFaultNum = 0
						cleanResident(residentSet,useBitSet)
						minVSWS = min(minVSWS, len(residentSet))
				# then add the current page fault to the resident set and append one to usebitset
				residentSet.append(pageUsing)
				useBitSet.append(1)
			i += 1
	print('VSWS')
	print 'MIN:',minVSWS
	print 'MAX:',maxVSWS
	print 'total number of page fault is ', totalPageFault




if __name__ == '__main__':
	#createFile()
	#pff(residentSet, useBitSet)
	vsws(residentSet, useBitSet)
	
	
