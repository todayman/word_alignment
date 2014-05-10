__author__ = 'tejasvamsingh'

from HMMParameterInitializer import initializeParameters
from HMMLikelihoodEstimator import ComputeDataLikelihood
from HMMParameterTrainer import TrainParameters

def ComputeAlignments(hiddenStatesList,observationsList):

    emissionProbabilityDict , transitionProbabilityDict = initializeParameters(hiddenStatesList,observationsList)


    forwardProbabilityDict,backwardProbabilityDict, dataLikelihood = ComputeDataLikelihood(hiddenStatesList,
                                                                                           observationsList,
                                                                                           emissionProbabilityDict,transitionProbabilityDict)

    emissionProbabilityDict,transitionProbabilityDict = TrainParameters(hiddenStatesList,observationsList,
                                                        emissionProbabilityDict,transitionProbabilityDict,
                                                        forwardProbabilityDict,backwardProbabilityDict,dataLikelihood)





