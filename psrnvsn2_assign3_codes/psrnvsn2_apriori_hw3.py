#!/usr/bin/python
# Code to implement the Apriori Algorithm
# Pramod Srinivasan (netid: psrnvsn2)
# Input files : Topic files and vocabulary mapping
# Output files are generated in the "../psrnvsn2_assign3_results/patterns/" "../psrnvsn2_assign3_results/max/" 
# and "../psrnvsn2_assign3_results/closed/" directories
# Execution:
#	python psrnvsn2_apriori_hw3.py <min_support_value> 
#
# If no min_support value is passed as a command line argument then the default value of 0.01 is used.
#

import itertools
from itertools import combinations
import collections
import inspect
import operator
import sys
import os
import math


vFile  = 'vocab.txt'
patterns_location = "../psrnvsn2_assign3_results/patterns/"
max_patterns_location = "../psrnvsn2_assign3_results/max/"
closed_patterns_location = "../psrnvsn2_assign3_results/closed/"
topic_files_location  = "../data/"
topic_files = ['topic-0.txt','topic-1.txt','topic-2.txt','topic-3.txt','topic-4.txt']

def record_Frequent_pattern(vocabMapTerms,patternFile):
   f = open(patternFile,'w')
   for termList,support in vocabMapTerms:
   	    line = str(support) +  ' ' 
   	    for term in termList:
   	    	line =  line + term +' ' 
   	    line = line + '\n'
   	    f.write(line)

#This function stores the mapping provided in the vocab.txt file to a dictionary 
#Each element of vocabMap is a (key,val) pair
def generate_vocabMap(vFile):
   vocabMap = {}
   with open(vFile) as f:
       for line in f: 
           (key, val) = line.split()
           vocabMap[int(key)] = val
   return vocabMap

#This function is used to generate the mapping between the term-ID and the term from vocab.txt
def mapVocabTerms(vFile,frequentItems):
	vocabMap = generate_vocabMap(vFile)
	vocabMappedValues = []
	for (fItemList, support) in frequentItems:
		v = []
		for term in fItemList:
			v.append(vocabMap[term])
		vocabMappedValues.append((v,support))
	return vocabMappedValues

#This function is used to record the closed frequent itemsets to a file.
def generateClosedItemSet(frequentItems):
	closedItems = []
	for fItem,support in frequentItems:
		flag = True
		for f2,sup2 in frequentItems:
			if set(fItem) < set(f2):
				if sup2 >= support:
					flag = False
		if flag == True:
			closedItems.append((fItem,support))
	return closedItems			

#This function is used to record the max frequent itemsets to a file.
def generateMaximalItemSet(frequentItems):
	maxItems = []
	for fItem,support in frequentItems:
		flag = True
		for f2,sup2 in frequentItems:
			if set(fItem) < set(f2):
				flag = False
		if flag == True:
			maxItems.append((fItem,support))
	return maxItems

#This function is used to store the transaction database from the topic file
def generate_transactions (tfile):
    topic_file = open(tfile,'r')
    transactions = []
    with open(tfile, "r") as splitfile:
         for transaction in [rawtransaction.split() for rawtransaction in splitfile]:
            transaction = map(int, transaction)
            transaction.sort()
            transactions.append(transaction)
    return transactions

#This function is used to generate the initial candidate set(C1) from the transaction
def generate_C1 (tr):
	transactions = []
	for i in tr:
		transactions = transactions + i
	d = {x:transactions.count(x) for x in transactions}
	uniq, freq = d.keys(), d.values()
	uniq_l = [[i] for i in uniq]
	C1 = zip(uniq_l, freq)
	return C1

#This function is used to generate the initial (Level 1) frequent set based on the Candidate itemset(C1) and min_support criterion
def generate_L1 (C1, min_support):
	L1 = []
	for (k,v) in C1:
		if v >= min_support:
			L1.append((k,v))
	return L1
	
def has_infrequent_subset(k, candidate_k, Lk_m_1):
	Lk_minus_1 = [sorted(key) for (key,v) in Lk_m_1]
	flag = False
	for i in range(0, k):
		candidate_k_1 = []
		for j in range(0, k):
			if j != i:
				candidate_k_1.append(candidate_k[j])
		candidate_k_1 = sorted(candidate_k_1)
		if not(candidate_k_1 in Lk_minus_1):
			flag = True
			break
	return flag

#The function generates C_k from the L_(k-1)
def apriori_gen(k_minus_1, Lk_minus_1):
	C_k = []
	for (l1, val1) in Lk_minus_1:
		for (l2, val2) in Lk_minus_1:
			flag = True
			for i in range(0, k_minus_1-1):
				flag &= (l1[i] == l2[i])
				if not flag:
					break
			flag &= (l1[k_minus_1-1] < l2[k_minus_1-1])
			if flag:
				c = sorted(list(set(l1 + l2)))
				if not has_infrequent_subset(k_minus_1+1, c, Lk_minus_1):
					C_k.append(c)
	return C_k

#The function which is used to generate the candidate itemset(C_k) and the frequent itemset at every level
#This function implements the apriori algorithm
def apriori (tfile, min_support):
	transactions = generate_transactions(tfile)
	C1 = generate_C1(transactions)
	L1 = generate_L1(C1,min_support)
	k = 1
	L_k = L1
	L = [L1]
	while True:
		Lk_minus_1 = L_k
		C_k_keys = apriori_gen(k, Lk_minus_1)
		C_k = []
		L_k = []
		for c in C_k_keys:
			val = 0
			for t in transactions:
				if set(c) <= set(t):
					val = val + 1
			C_k.append((sorted(c),val))
			if val >= min_support:
				L_k.append((sorted(c),val))
		if not L_k:
			break
		L.append(L_k)
		k = k +1
	frequentItems = []
	for l in L:
		for (key, val) in l:
			frequentItems.append((key,val))
	print "The Frequent Itemset L for has been recorded."
	return frequentItems


if __name__ == "__main__":
	if (len(sys.argv) == 2):
		min_support = float(sys.argv[1])
	min_support = 100
	print "Running Apriori Algorithm with min_support = " + str(min_support)
	if not os.path.exists(patterns_location):
			os.makedirs(patterns_location)
	if not os.path.exists(max_patterns_location):
			os.makedirs(max_patterns_location)
	if not os.path.exists(closed_patterns_location):
			os.makedirs(closed_patterns_location)
	vFile = topic_files_location + vFile
        i = 0
	for tfile in topic_files: 
		print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
		print "Processing File " + tfile  + " to generate frequent patterns"
		tfile = topic_files_location + tfile
		patternFile = patterns_location + "pattern-" + str(i) + ".txt"
		closeFile   = closed_patterns_location + "closed-" + str(i) + ".txt"
		maxFile     = max_patterns_location + "max-" + str(i) + ".txt"
		i = i+1
		frequentItems = apriori(tfile, min_support) 
		frequentItems = sorted(frequentItems,key=operator.itemgetter(1),reverse=True)
		vocabMapTerms = mapVocabTerms(vFile,frequentItems)
		record_Frequent_pattern(vocabMapTerms,patternFile)
		print "Recorded the frequent itemset L in " + patternFile + "."
		closedItems = generateClosedItemSet(frequentItems)
		vocabMappedClosedItems = mapVocabTerms(vFile,closedItems)
		record_Frequent_pattern(vocabMappedClosedItems,closeFile)
		print "Recorded the closed frequent patterns in " + closeFile + "."
		maxItems  = generateMaximalItemSet(frequentItems)
		vocabMappedMaxItems = mapVocabTerms(vFile,maxItems)
		record_Frequent_pattern(vocabMappedMaxItems,maxFile)
		print "Recorded the maximal patterns in " + maxFile + "."
