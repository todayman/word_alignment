__author__ = 'tejasvamsingh'


import sys
from math import log

class HMMViterbiDecoder:

    def __init__(self,transitionProbabilityDict,emissionProbabilityDict,distanceParameter):
        self.transitionProbabilityDict = transitionProbabilityDict
        self.emissionProbabilityDict = emissionProbabilityDict
        self.distanceParameter = distanceParameter

    def Decode(self, hiddenStatesList, observationsList ):
        
        backPointerDict={}
        viterbiProbabilityDict={}
        self.GenerateViterbiLattice(backPointerDict,viterbiProbabilityDict,hiddenStatesList,observationsList)
        return self.ExtractViterbiPath(backPointerDict,viterbiProbabilityDict,hiddenStatesList,observationsList)


    def GenerateViterbiLattice(self,backPointerDict, viterbiProbabilityDict ,hiddenStatesList, observationsList):


        viterbiProbabilityDict[-1] = {}
        viterbiProbabilityDict[-1]["<s>"]=0.0

        observationLength = len(hiddenStatesList) * len(observationsList)
        hiddenstatesLength = len(hiddenStatesList)
    
        for timeStep in xrange(0,len(observationsList)):
            backPointerDict[timeStep]={}
            viterbiProbabilityDict[timeStep]={}
            for hiddenStateIndex in xrange(0,hiddenstatesLength):
                hiddenState = hiddenStatesList[hiddenStateIndex]
                try:
                    x = ( log(self.emissionProbabilityDict[(observationsList[timeStep],hiddenState)]))
                except:
                    continue
                x=0
                try:
                    x=log(pow(self.distanceParameter,abs(hiddenStateIndex-timeStep)))
                except:
                    x=0


                viterbiProb = - sys.maxint
                bestState = ""
                for previousState in viterbiProbabilityDict[timeStep-1].keys():
                    previousStateViterbiProbability = viterbiProbabilityDict[timeStep-1][previousState]


                    try:
                        yV = (log(self.transitionProbabilityDict[observationLength][(hiddenState,previousState)]))
                    except:
                        continue



                    if previousStateViterbiProbability + log(self.transitionProbabilityDict[observationLength][(hiddenState,previousState)]) + x > viterbiProb:
                        viterbiProb = previousStateViterbiProbability + log(self.transitionProbabilityDict[observationLength][(hiddenState,previousState)]) +x
                        bestState = previousState


    
                viterbiProb = viterbiProb + log(self.emissionProbabilityDict[(observationsList[timeStep],hiddenState)])
                viterbiProbabilityDict[timeStep][hiddenState]=viterbiProb
                backPointerDict[timeStep][hiddenState] = bestState


    
        # transition to the end state </s>
    
        viterbiProb = - sys.maxint
        bestState = hiddenStatesList[0]
        for previousState in viterbiProbabilityDict[len(observationsList)-1].keys():
            previousStateViterbiProbability = viterbiProbabilityDict[len(observationsList)-1][previousState]
            try:
                if previousStateViterbiProbability + log(self.transitionProbabilityDict[observationLength][("</s>",previousState)]) > viterbiProb:
                    viterbiProb = previousStateViterbiProbability + log(self.transitionProbabilityDict[observationLength][("</s>",previousState)])
                    bestState = previousState
            except:
                continue

        viterbiProbabilityDict[len(observationsList)] ={}
        viterbiProbabilityDict[len(observationsList)]["</s>"]=viterbiProb
        backPointerDict[len(observationsList)]={}
        backPointerDict[len(observationsList)]["</s>"] = bestState


    def ExtractViterbiPath(self,backPointerDict, viterbiProbabilityDict, hiddenStatesList, observationsList):

        hiddenStateObservationStateSequence =""
        hiddenState = backPointerDict[len(observationsList)]["</s>"]
        for timeStep in xrange(len(observationsList)-1,-1,-1):
            hiddenStateObservationStateSequence = hiddenStateObservationStateSequence + (str(timeStep)+"-"+
                                                                                         str(hiddenStatesList.index(hiddenState))+" ")
            hiddenState = backPointerDict[timeStep][hiddenState]


        return hiddenStateObservationStateSequence.rstrip()







    
