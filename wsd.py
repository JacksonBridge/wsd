# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# wsd.py
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Jackson Hambridge
# CMSC 416 Spring 2020
# 3/30/2020
#
# This program predicts word sense with different features. It trains
# on a file and will predict another file. It uses multiple features, such as:
# w-1, w-2, w-2w-1, w-1w+1, w+1, w+2, w+1w+2
# Words can have different meaning depending on context, such as
# a baseball bat versus a vampire bat. This program works to differntiate
# between word senses.
# 
# One example of how the program can run:
# py wsd.py line-train.txt line-test.txt my-model.txt > my-line-answers.txt
# It will output the dictionary that stores 
#
# The algorithm uses Decision Lists to sort each type of feature and feature
# to assign discriminative values. The most discriminative features will be used
# first to predict the sense.
#

import re
import math
import copy
import sys

# This method adds an item to the dictionary
def updateDictionary(featureCorpus,featureType,feature,sense):
    if not featureCorpus[featureType]:
        senseDictionary={sense:1}
        featureDictionary={feature:senseDictionary}
        featureCorpus[featureType]=featureDictionary
    else:
        if feature not in featureCorpus[featureType]:
            senseDictionary={sense:1}
            featureCorpus[featureType][feature]=senseDictionary
        else:
            if sense not in featureCorpus[featureType][feature]:
                featureCorpus[featureType][feature][sense]=1
            else:
                featureCorpus[featureType][feature][sense]+=1
    return featureCorpus

# This method finds the most discriminative feature
def findBestFeature(discriminativeDictionary, wDict):
    maximum=0
    bestFeatureType="failure"
    bestFeature="failure"
    for featureType, feature in wDict.items():
        if feature in discriminativeDictionary[featureType]:
            if discriminativeDictionary[featureType][feature]["discriminative"]>maximum:
                maximum = discriminativeDictionary[featureType][feature]["discriminative"]
                bestFeatureType=featureType
                bestFeature=feature
    return (bestFeatureType,bestFeature)

# Gather command line arguments
if len(sys.argv) == 1:
    trainingFile="line-train.txt"
    testFile="line-test.txt"
    modelFile="my-model.txt"
elif len(sys.argv) == 2:
    trainingFile=sys.argv[1]
    testFile="line-test.txt"
    modelFile="my-model.txt"
elif len(sys.argv) == 3:
    trainingFile=sys.argv[1]
    testFile=sys.argv[2]
    modelFile="my-model.txt"
else:
    trainingFile=sys.argv[1]
    testFile=sys.argv[2]
    modelFile=sys.argv[3]

# Read training file
file=open(trainingFile,'r',encoding = 'utf-8')
trainingCorpus=file.read().lower()
file.close()

# Process training file
trainingCorpus=re.sub("<s>","",trainingCorpus)
trainingCorpus=re.sub("</s>","",trainingCorpus)
trainingCorpus=re.sub("<p>","",trainingCorpus)
trainingCorpus=re.sub("</p>","",trainingCorpus)
trainingCorpus=re.sub("<@>","",trainingCorpus)
trainingCorpus=re.sub("</@>","",trainingCorpus)
trainingCorpus=re.sub("\,"," , ",trainingCorpus)
trainingCorpus=re.sub("\."," <end> ",trainingCorpus)
trainingCorpus=re.sub("\?"," <end> ",trainingCorpus)
trainingCorpus=re.sub("\!"," <end> ",trainingCorpus)

trainingCorpus=str.split(trainingCorpus,"</instance>")

# Prepare dictionary
featureCorpus={
    "w-1":{},
    "w-2":{},
    "w+1":{},
    "w+2":{},
    "w-2,w-1":{},
    "w+1,w+2":{},
    "w-1,w+1":{}
}

# Prepare sense count
senseCount={
    "phone":0,
    "product":0
}

# Loop through corpus
for elements in trainingCorpus:
    # If the instance id is on this line, split it by \n
    if "<instance id=" in elements:
        elements=str.split(elements,"\n")
        for line in elements:
            # If the ID is on this line, gather ID
            if "<instance id=" in line:
                instanceID=line
                instanceID=re.sub("<instance id=\"","",instanceID)
                instanceID=re.sub("\">","",instanceID)
            # If sense is on this line, gather sense
            if "senseid=" in line:
                senseID=line
                senseID=re.sub(".*senseid=\"","",senseID)
                senseID=re.sub("\"/>","",senseID)
                senseCount[senseID]+=1
            # If head is on this line, calculate features
            if "<head>" in line:
                context=str.split(line)
                count=0
                w=0

                # Find the head's position
                for word in context:
                    if "<head>" in word:
                        w=count
                    count+=1
                
                sense=senseID
                sentenceStart=0
                sentenceEnd=len(context)

                # Calculate features and add them to dicitonary featureCorpus

                # Feature: w-1
                # The previous word
                if w-1 >= sentenceStart:
                    featureType="w-1"
                    feature=context[w-1]
                    featureCorpus=updateDictionary(featureCorpus,featureType,feature,sense)
                
                # Feature: w-2
                # Two words previous
                if w-2 >= sentenceStart:
                    featureType="w-2"
                    feature=context[w-2]
                    featureCorpus=updateDictionary(featureCorpus,featureType,feature,sense)

                    # Feature: w-2,w-1
                    # The previous ngram of size two
                    featureType="w-2,w-1"
                    feature=context[w-2] + " " + context[w-1]
                    featureCorpus=updateDictionary(featureCorpus,featureType,feature,sense)

                # Feature: w+1
                # The following word
                if w+1 < sentenceEnd:
                    featureType="w+1"
                    feature=context[w+1]
                    featureCorpus=updateDictionary(featureCorpus,featureType,feature,sense)

                # Feature: w+2
                # Two words after
                if w+2 < sentenceEnd:
                    featureType="w+2"
                    feature=context[w+2]
                    featureCorpus=updateDictionary(featureCorpus,featureType,feature,sense)

                    # Feature: w+1,w+2
                    # The following ngram of size 2
                    featureType="w+1,w+2"
                    feature=context[w+1] + " " + context[w+2]
                    featureCorpus=updateDictionary(featureCorpus,featureType,feature,sense)

                # Feature: w-1,w+1
                # The surrounding words
                if w+1 < sentenceEnd and w-1 >= sentenceStart:
                    featureType="w-1,w+1"
                    feature=context[w-1] + " " + context[w+1]
                    featureCorpus=updateDictionary(featureCorpus,featureType,feature,sense)

# Get all feature types and features
discriminativeDictionary=copy.deepcopy(featureCorpus)

# Loop through and calculate the discriminative
for featureType in featureCorpus:
    for feature in featureCorpus[featureType]:
        if "phone" in featureCorpus[featureType][feature] and "product" in featureCorpus[featureType][feature]:
            discriminativeDictionary[featureType][feature]["discriminative"]=abs(math.log( ( featureCorpus[featureType][feature]["phone"] )/( featureCorpus[featureType][feature]["product"] ) ))
            if featureCorpus[featureType][feature]["phone"] > featureCorpus[featureType][feature]["product"]:
                discriminativeDictionary[featureType][feature]["bestSense"]="phone"
            elif featureCorpus[featureType][feature]["phone"] < featureCorpus[featureType][feature]["product"]:
                discriminativeDictionary[featureType][feature]["bestSense"]="product"
        else:
            # If "product" doesn't exist
            if "phone" in featureCorpus[featureType][feature]:
                discriminativeDictionary[featureType][feature]["discriminative"]=10000*featureCorpus[featureType][feature]["phone"]
                discriminativeDictionary[featureType][feature]["bestSense"]="phone"
                featureCorpus[featureType][feature]["product"]=0
            # If "phone" doesn't exist
            else:
                discriminativeDictionary[featureType][feature]["discriminative"]=10000*featureCorpus[featureType][feature]["product"]
                discriminativeDictionary[featureType][feature]["bestSense"]="product"
                featureCorpus[featureType][feature]["phone"]=0

# Read the test file
file=open(testFile,'r',encoding = 'utf-8')
testingCorpus=file.read().lower()
file.close()

# Process test file
testingCorpus=re.sub("<s>","",testingCorpus)
testingCorpus=re.sub("</s>","",testingCorpus)
testingCorpus=re.sub("<p>","",testingCorpus)
testingCorpus=re.sub("</p>","",testingCorpus)
testingCorpus=re.sub("<@>","",testingCorpus)
testingCorpus=re.sub("</@>","",testingCorpus)

testingCorpus=str.split(testingCorpus,"</instance>")

senseDict={}

# Follow a similar algorithm to calculate instance and sense
for elements in testingCorpus:
    if "<instance id=" in elements:
        elements=str.split(elements,"\n")
        for line in elements:
            if "<instance id=" in line:
                instanceID=line
                instanceID=re.sub("<instance id=\"","",instanceID)
                instanceID=re.sub("\">","",instanceID)
            if "<head>" in line:
                tempDiscriminativeDictionary=copy.deepcopy(discriminativeDictionary)
                context=str.split(line)
                count=0
                w=0
                for word in context:
                    if "<head>" in word:
                        w=count
                    count+=1
                
                sense=senseID
                sentenceStart=0
                sentenceEnd=len(context)

                wDict={}

                # Calculate features
                if w-1 >= sentenceStart:
                    wDict["w-1"]=context[w-1]                
                if w-2 >= sentenceStart:
                    wDict["w-2"]=context[w-2]

                    wDict["w-2,w-1"]=context[w-2] + " " + context[w-1]

                if w+1 < sentenceEnd:
                    wDict["w+1"]=context[w+1]

                if w+2 < sentenceEnd:
                    wDict["w+2"]=context[w+2]

                    wDict["w+1,w+2"]=context[w+1] + " " + context[w+2]

                if w+1 < sentenceEnd and w-1 >= sentenceStart:
                    wDict["w-1,w+1"]=context[w-1] + " " + context[w+1]

                found=0

                # Loop until a prediction is found
                while found == 0:
                    # Calculate best feature
                    (bestFeatureType,bestFeature)=findBestFeature(tempDiscriminativeDictionary,wDict)
                    # If there is absolutely no best feature
                    if bestFeatureType == "failure":
                        if senseCount["phone"] > senseCount["product"]: #Majority sense
                            bestSense="phone"
                        else:
                            bestSense="product"
                        senseDict[instanceID]=bestSense
                        found=1
                    else:
                        # Set this feature to zero (so it cannot be found again)
                        tempDiscriminativeDictionary[bestFeatureType][bestFeature]["discriminative"]=0
                        # If the best feature type is in our dictionary
                        if bestFeatureType in wDict:
                            # If the best feature is in our dictionary
                            if bestFeature is wDict[bestFeatureType]:
                                # We found it!
                                found=1
                                # Find the majority sense predicted with that feature
                                if featureCorpus[bestFeatureType][bestFeature]["phone"] > featureCorpus[bestFeatureType][bestFeature]["product"]:
                                    bestSense="phone"
                                else:
                                    bestSense="product"
                                # Add it to our dictionary
                                senseDict[instanceID]=bestSense

# Print senseDict to standard output
for instance in senseDict:
    print("<answer instance=\"" + instance + "\" senseid=\"" + senseDict[instance] + "\"/>")

# Output the Decision List
f = open(modelFile, "w")
f.write(str(discriminativeDictionary))
f.close()