import warnings
from operator import itemgetter
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    for word_id in range(test_set.num_items):
        # compute the log likelihood of the test item for each word model
        log_likelihoods = {}
        for word, model in models.items():
            # apparently, the hmmlearn library is not able to train or score all models,
            # so we just assign a probability of 0 to the models for which we get an exception
            try:
                log_likelihoods[word] = model.score(*test_set.get_item_Xlengths(word_id))
            except ValueError:
                log_likelihoods[word] = float("-inf")
                
        probabilities.append(log_likelihoods)
        guesses.append(max(log_likelihoods.items(), key=itemgetter(1))[0])
        
    return probabilities, guesses
