__author__ = 'tejasvamsingh'

from HMMParameterInitializer import initializeParameters
from HMMLikelihoodEstimator import HMMLikelihoodEstimator
from HMMParameterTrainer import HMMParameterTrainer
from HMMViterbiDecoder import HMMViterbiDecoder


class HMMAlignmentHander:

    def __init__(self,hiddenStatesList,observationsList):
        self.emissionProbabilityDict={}
        self.transitionProbabilityDict={}
        self.uniformEmissionProbability = float(1)/float(len(observationsList))
        self.uniformTransitionProbability = float(1)/float(len(hiddenStatesList))

    def TrainAligner(self,hiddenStatesLists,observationsLists):

        hmmLikelihoodEstimatorObject  = HMMLikelihoodEstimator(self.uniformEmissionProbability,self.uniformTransitionProbability)

        for iterationNumber in xrange(0,5):
            numSentences=0
            hmmParameterTrainerObject = HMMParameterTrainer()

            for hiddenStatesList,observationsList in zip(hiddenStatesLists,observationsLists):

                if numSentences==1000:
                    break

                numSentences =numSentences+1


                forwardProbabilityDict,backwardProbabilityDict, dataLikelihood = hmmLikelihoodEstimatorObject.ComputeDataLikelihood(hiddenStatesList,
                                                                                                       observationsList,
                                                                                                       self.emissionProbabilityDict,
                                                                                                       self.transitionProbabilityDict,)

                hmmParameterTrainerObject.ExpectationStep(hiddenStatesList,observationsList,
                                                          self.emissionProbabilityDict,self.transitionProbabilityDict,
                                                          forwardProbabilityDict,backwardProbabilityDict,dataLikelihood)

            hmmParameterTrainerObject.MaximizationStep(self.transitionProbabilityDict,self.emissionProbabilityDict)


    def ComputeAlignments(self,hiddenStatesLists,observationsLists):

        hmmViterbiDecoderObject = HMMViterbiDecoder(self.transitionProbabilityDict,self.emissionProbabilityDict)
        alignmentList = []

        for hiddenStatesList,observationsList in zip(hiddenStatesLists,observationsLists):
            alignmentList.append(hmmViterbiDecoderObject.Decode(hiddenStatesList,observationsList))

        return alignmentList















