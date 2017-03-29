import math
import statistics
import warnings
import sys

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except ValueError:
            if self.verbose:
                print("hmmlearn failed to train model on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Baysian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        bic_scores = []

        for n_components in range(self.min_n_components, self.max_n_components):
            # apparently, the hmmlearn library is not  able to train or score all models,
            # so we just skip the models for which we get an exception
            try:
                hmm_model = GaussianHMM(n_components=n_components, covariance_type="diag", n_iter=1000,
                                        random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
                log_L = hmm_model.score(self.X, self.lengths) # log likelihood
                log_N = math.log(len(self.X)) # log of the number of data points
                # nb of parameters of the model = 2 * nb features * nb components (mean and std of each state) 
                #                                + nb components (transition probabilities)
                p = n_components * (1 + 2*len(hmm_model.means_[0]))
                bic = -2 * log_L + p * log_N
                bic_scores.append((bic, n_components))
            except ValueError:
                if self.verbose:
                    print("hmmlearn failed to train model on {} with {} states".format(self.this_word, num_states))

        # Use the number of components that minimizes the bic score
        best_num_components = self.min_n_components
        if len(bic_scores) > 0:
            best_num_components = min(bic_scores)[1]

        return self.base_model(best_num_components)

class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        other_words = set(self.words.keys())
        other_words.discard(self.this_word)
        dic_scores = []

        for n_components in range(self.min_n_components, self.max_n_components):
            # apparently, the hmmlearn library is not able to train or score all models,
            # so we just skip the models for which we get an exception
            try:
                hmm_model = GaussianHMM(n_components=n_components, covariance_type="diag", n_iter=1000,
                                        random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
                log_likelihood = hmm_model.score(self.X, self.lengths)  # log likelihood
                log_antilikelihood = np.average([hmm_model.score(*self.hwords[w]) for w in other_words])
                dic = log_likelihood - log_antilikelihood
                dic_scores.append((dic, n_components))
            except ValueError:
                if self.verbose:
                    print("hmmlearn failed to train model on {} with {} states".format(self.this_word, num_states))

        # Use the number of components that maximizes the bic score
        best_num_components = self.min_n_components
        if len(dic_scores) > 0:
            best_num_components = max(dic_scores)[1]

        return self.base_model(best_num_components)

class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self, max_nb_folds=5):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # If we don't have enough exemple for k-folds, just return a model with the minimum number of components
        if len(self.sequences) < 2:
            return self.base_model(self.min_n_components)
        
        # Prepare k-folds training and testing sets
        nb_splits = min(max_nb_folds, len(self.sequences))
        split_method = KFold(n_splits=nb_splits)
        cv_train_folds, cv_test_folds = [], []
        for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
            cv_train_folds.append(combine_sequences(cv_train_idx, self.sequences))
            cv_test_folds.append(combine_sequences(cv_test_idx, self.sequences))

        # Measure average log likelihood over the folds for each possible number of components
        average_log_likelihoods = []
        for n_components in range(self.min_n_components, self.max_n_components):
            log_likelihoods = []
            for split_no in range(nb_splits):
                # apparently, the hmmlearn library is not be able to train or score all models,
                # so we just skip the models for which we get an exception
                try:
                    hmm_model = GaussianHMM(n_components=n_components, covariance_type="diag", n_iter=1000,
                                        random_state=self.random_state, verbose=False).fit(*cv_train_folds[split_no])
                    log_likelihoods.append(hmm_model.score(*cv_test_folds[split_no]))
                except ValueError:
                    if self.verbose:
                        print("hmmlearn failed to train model on {} with {} states".format(self.this_word, num_states))

            if len(log_likelihoods) > 0:
                average_log_likelihoods.append((np.average(log_likelihoods), n_components))

        # Use the number of components that maximise the average log likelihood
        best_num_components = self.min_n_components
        if len(average_log_likelihoods) > 0:
            best_num_components = max(average_log_likelihoods)[1]

        return self.base_model(best_num_components)
