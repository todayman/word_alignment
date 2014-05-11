__author__ = 'tejasvamsingh'

from HMMParameterInitializer import initializeParameters
from HMMLikelihoodEstimator import ComputeDataLikelihood
from HMMParameterTrainer import HMMParameterTrainer
from HMMViterbiDecoder import HMMViterbiDecoder


class HMMAlignmentHander:

    def __init__(self,hiddenStatesList,observationsList):
        self.emissionProbabilityDict,self.transitionProbabilityDict=\
            initializeParameters(hiddenStatesList,observationsList)

    def TrainAligner(self,hiddenStatesLists,observationsLists):

        for iterationNumber in xrange(0,5):

            hmmParameterTrainerObject = HMMParameterTrainer()

            for hiddenStatesList,observationsList in zip(hiddenStatesLists,observationsLists):


                forwardProbabilityDict,backwardProbabilityDict, dataLikelihood = ComputeDataLikelihood(hiddenStatesList,
                                                                                                       observationsList,
                                                                                                       self.emissionProbabilityDict,
                                                                                                       self.transitionProbabilityDict)

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















