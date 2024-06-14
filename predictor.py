import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, SGDRegressor

from predictor_base import Predictor
from util import Candidate

class PrevVotePredictor(Predictor):
    def __init__(self, data, dates, name):
        super().__init__(data, dates, name)

    def predict(self, d_i: int, city: str, district_name: str):
        return self.get_base_vote(d_i, city, district_name)
    
class LRPredictor(Predictor):
    def __init__(self, data, dates, name, param):
        super().__init__(data, dates, name)
        self.model = LinearRegression(fit_intercept=False)
        for p in param:
            if p not in ['prev_vote', 'trend', 'sentiment', 'pos_sentiment', 'neg_sentiment']:
                raise Exception
            
        self.param = param

    def calc_factors(self, trend, sentiment):
        t_factor, p_st_factor, n_st_factor = 0, 0, 0
        for day, (t, s) in enumerate(zip(trend[:-2], sentiment[:-2])):
            t_factor += 0.2 * t

            if s < 0:
                n_st_factor += 0.2 * t * s
            else:
                p_st_factor += 0.2 * t * s
        
        return t_factor, p_st_factor, n_st_factor
    
    def prepare_feature(self, c_pred: Candidate, sentiment: pd.DataFrame):
        feature = []
        t_factor, p_st_factor, n_st_factor = 0, 0, 0

        if c_pred.name in sentiment.columns:
            t_factor, p_st_factor, n_st_factor = self.calc_factors(sentiment[c_pred.name], sentiment[f'{c_pred.name}_sentiment'])

        if 'prev_vote' in self.param:
            feature.append(c_pred.votes)
        
        if 'trend' in self.param:
            feature.append(t_factor)

        if 'sentiment' in self.param:
            feature.append(p_st_factor + n_st_factor)

        if 'pos_sentiment' in self.param:
            feature.append(p_st_factor)

        if 'neg_sentiment' in self.param:
            feature.append(n_st_factor)

        return feature

    def train(self):
        x = []
        y = []

        for d_i in range(1, len(self.dates)):
            for city in self.data[d_i].keys():
                for district_name in self.data[d_i][city].keys():
                    try:
                        sentiment = pd.read_csv(f'sentiment_google\\{self.dates[d_i]}_{city}_{district_name}.csv')
                    except Exception:
                        continue
                    
                    pred = self.get_base_vote(d_i, city, district_name)
                    real = self.data[d_i][city][district_name]

                    for c_real, c_pred in zip(real, pred):
                        feature = self.prepare_feature(c_pred, sentiment)
                        x.append(feature)
                        y.append(c_real.votes)

        x = np.array(x)
        y = np.array(y)
        self.model.fit(x, y)

    def predict(self, d_i: int, city: str, district_name: str):
        base = self.get_base_vote(d_i, city, district_name)
        try:
            sentiment = pd.read_csv(f'sentiment_google\\{self.dates[d_i]}_{city}_{district_name}.csv')
        except Exception:
            return base
        
        prediction = []
        for candidate in base:
            feature = self.prepare_feature(candidate, sentiment)
            in_arr = np.array(feature).reshape((1, len(feature)))
            p_votes = self.model.predict(in_arr)
            prediction.append(Candidate(candidate.party, candidate.name, p_votes))
            
        return prediction
    
    def get_coeff(self):
        return self.model.coef_
        