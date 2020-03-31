# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# scorer.py
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Jackson Hambridge
# CMSC 416 Spring 2020
# 3/30/2020 
# 
# This program uses the output from wsd.py and compares it to a key in order
# to score the prediction from wsd.py and give a confusion matrix.
# 
# One example of how the program can run:
# py scorer.py my-line-answers.txt line-key.txt
# This will output a confusion matrix as well as other information.
# 

import sys
import re

# Gather command line arguments
if len(sys.argv) == 1:
    predictionFile="my-line-answers.txt"
    keyFile="line-key.txt"
elif len(sys.argv) == 2:
    predictionFile=sys.argv[1]
    keyFile="line-key.txt"
else:
    predictionFile=sys.argv[1]
    keyFile=sys.argv[2]

# Read the key
with open(keyFile, 'r') as f:
    keyCorpus=f.read().lower()
f.close()

# Process the key to get instance and sense
keyCorpus=str.split(keyCorpus,"\n")
keyDict={}
for line in keyCorpus:
    if "answer" in line:

        instanceID=line
        instanceID=re.sub(".*instance=\"","",instanceID)
        instanceID=re.sub("\".*","",instanceID)

        senseID=line
        senseID=re.sub(".*senseid=\"","",senseID)
        senseID=re.sub("\".*","",senseID)

        keyDict[instanceID]=senseID

# Read the predictions
with open(predictionFile, encoding="utf8", errors='ignore') as j:
    predictionCorpus=j.read().lower()
j.close()

# Process the predictions to get instance and sense
predictionCorpus=re.sub("\x00","",predictionCorpus)
predictionCorpus=str.split(predictionCorpus,"\n")
predictionDict={}
for line in predictionCorpus:
    instanceID=line
    instanceID=re.sub(".*instance=\"","",instanceID)
    instanceID=re.sub("\".*","",instanceID)

    senseID=line
    senseID=re.sub(".*senseid=\"","",senseID)
    senseID=re.sub("\".*","",senseID)

    predictionDict[instanceID]=senseID

# Set variabless
correct=0
incorrect=0
prod=0
phon=0
accuracy=0
actuallyPhon=0
actuallyProd=0

# Compare prediction and key given an instance
for key in keyDict:
    if predictionDict[key] != "N/A":
        if predictionDict[key] == keyDict[key]:
            correct+=1
            if predictionDict[key] == "phone":
                phon+=1
            else:
                prod+=1
        else:
            incorrect+=1
            if keyDict[key] == "phone":
                actuallyPhon+=1
            else:
                actuallyProd+=1

# Calculate accuracy
accuracy=correct/(correct+incorrect) * 100

# Print information
print()
print("Correct Predictions: " + str(correct))
print("Incorrect Predictions: " + str(incorrect))
print("Predicted phone correctly: " + str(phon))
print("Predicted product correctly: " + str(prod))
print()
print("Accuracy: " + str(accuracy))
print()
# Print and format confusion matrix
print("        \Actual         phone    product")
print("Predicted\     phone    "+str(phon)+"       "+str(actuallyProd))
print("               product  "+str(actuallyPhon)+"       "+str(prod))