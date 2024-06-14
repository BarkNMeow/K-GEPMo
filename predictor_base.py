from matplotlib import pyplot as plt
from matplotlib import rc
import numpy as np

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

from util import Candidate

rc('font', family='NanumGothic')

class Predictor:
    def __init__(self, data, dates, name):
        self.data = data
        self.dates = dates
        self.name = name

    def predict(self, d_i, city, district_name):
        pass

    def party_to_spectrum(self, d_i: int, city: str, candidate: Candidate) -> list[int]:
        f = open(f'election_change\\{self.dates[d_i]}-party.csv', 'r', encoding='UTF-8')
        result = []
        for line in f:
            line = line.split(',')

            if line[0] == candidate.party:
                if candidate.party != '무소속':
                    result = list(map(int, line[3:]))
                    break
                if line[1] == city and line[2] == candidate.name:
                    result = list(map(int, line[3:]))
                    break
        
        f.close()
        return result

    def get_prev_district(self, d_i: int, city: str, district_name: str):
        prev_file = open(f'election_change\\{self.dates[d_i]}-district.csv', 'r')
        prev_city = city

        if d_i == 3:
            if city == '강원특별자치도':
                prev_city = '강원도'
            elif city == '전북특별자치도':
                prev_city = '전라북도'
            
        for line in prev_file:
            line = line.split(',')

            if line[0] == city and line[1] == district_name:
                result = []
                i = 2
                
                while i < len(line):
                    if d_i == 3 and line[i] == '군위군의성군청송군영덕군':
                        prev_city = '경상북도'
                            
                    result.append((prev_city, line[i], int(line[i + 1])))
                    i += 2
                return result
            
        return [(prev_city, district_name, 1)]

    def get_party_color(self, spectrums: list[int]):
        if len(spectrums) == 0:
            return (0.5, 0.5, 0.5)
        colors = np.array([[1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0]])
        spectrums = np.array(spectrums)

        return tuple(np.sum(colors[spectrums], axis=0) / len(spectrums))
    
    def get_seats(self):
        pred_bin = {}
        real_bin = {}

        for pred, real in  zip(self.prediction, self.real):
            pred_winner = self.get_winner(pred)
            real_winner = self.get_winner(real)

            pred_bin[pred_winner.party] = pred_bin.setdefault(pred_winner.party, 0) + 1
            real_bin[real_winner.party] = real_bin.setdefault(real_winner.party, 0) + 1

        return pred_bin, real_bin

    def get_winner(self, result: list[Candidate]):
        winner = result[0]

        for candidate in result:
            if candidate.votes > winner.votes:
                winner = candidate

        return winner

    def propagate_voters(self, base: int, vote_dist, curr: int):
        if len(vote_dist[curr]) > 0:
            return vote_dist[curr]
        
        new_vote_dist = []
        if curr >= base and curr + 1 < len(vote_dist):
            new_vote_dist.extend(self.propagate_voters(base, vote_dist, curr + 1))

        if curr <= base and curr - 1 >= 0:
            new_vote_dist.extend(self.propagate_voters(base, vote_dist, curr - 1))
        
        # Suppose the people supporting the spectrum moves to adjacent spectrum by 50-50
        # If no candidate exists
        return [(candidate, weight * 0.5) for (candidate, weight) in new_vote_dist]
    
    def get_base_vote(self, d_i: int, city: str, district_name: str) -> list[Candidate]:
        curr_data = self.data[d_i][city][district_name]

        # Get amount of votes that each spectrum got
        bucket = [0 for _ in range(5)]
        prev_districts = self.get_prev_district(d_i, city, district_name)
        center_exists = False
        
        for (prev_city, prev_district, weight) in prev_districts:
            for candidate in self.data[d_i - 1][prev_city][prev_district]:
                spectrums = self.party_to_spectrum(d_i - 1, prev_city, candidate)

                if candidate.party != '무소속' and (2 in spectrums):
                    center_exists = True

                for s in spectrums:
                    bucket[s] += weight * candidate.votes / len(spectrums)

        center_proportion = 0.15
        if not center_exists:
            bucket[2] = (bucket[1] + bucket[3]) * center_proportion
            bucket[1] *= (1 - center_proportion)
            bucket[2] *= (1 - center_proportion)
        
        # Calculate how is the vote is going to be distributed, based on spectrum
        vote_dist = [[] for _ in range(5)]
        for c_i, candidate in enumerate(curr_data):
            spectrums = self.party_to_spectrum(d_i, city, candidate)
            for s in spectrums:
                vote_dist[s].append((c_i, 1 / len(spectrums)))

        # For empty vote_dist bucket (which means no candidate), propagate voters to adjacent spectrum
        vote_dist_original = vote_dist[:]
        for s, d in enumerate(vote_dist):
            if len(d) == 0:
                self.propagate_voters(s, vote_dist_original, s)

        # Distribute the votes from the previous result to the result
        vote_prediction = [0.0 for _ in curr_data]
        for s, dist_list in enumerate(vote_dist):
            weight_sum = sum(map(lambda x: x[1], dist_list))
            for (c, weight) in dist_list:
                vote_prediction[c] += weight / weight_sum * bucket[s]

        # Normalize the sum
        vote_sum = sum(vote_prediction)
        for n in range(len(vote_prediction)):
            vote_prediction[n] /= vote_sum / 100

        result = []
        for c_i, candidate in enumerate(curr_data):
            prediction = vote_prediction[c_i]
            result.append(Candidate(candidate.party, candidate.name, prediction))
        
        return result
    
    def draw_scatter_plot(self):
        X = []
        Y = []
        colors = []
    

        for d_i in range(1, len(self.data)):
            real_list = []
            pred_list = []

            for city in self.data[d_i].keys():
                for district_name in self.data[d_i][city].keys():
                    prediction = self.predict(d_i, city, district_name)
                    result = self.data[d_i][city][district_name]

                    pred_list.append(prediction)
                    real_list.append(result)

                    colors.extend(map(lambda x: self.get_party_color(self.party_to_spectrum(d_i, city, x)), result))
                    X.extend(map(lambda x: x.votes, prediction))
                    Y.extend(map(lambda x: x.votes, result))

                    # Get candidate with most vote
                    prediction.sort(key=lambda x: x.votes, reverse=True)
                    result.sort(key=lambda x: x.votes, reverse=True)

        print(len(X))

        plt.xlim(-1, 101)
        plt.ylim(-1, 101)
        plt.title(f'{self.name}: prediction vs actual result')
        plt.xlabel('Prediction')
        plt.ylabel('Actual result')

        plt.plot((0, 100), (0, 100), 'k--')
        plt.scatter(X, Y, c=colors, alpha=0.3, edgecolors='none')

    def get_confusion_matrix(self, d_i: int):
        y_true = []
        y_pred = []
        seats = {}

        for city in self.data[d_i].keys():
            for district_name in self.data[d_i][city].keys():
                prediction = self.predict(d_i, city, district_name)
                real = self.data[d_i][city][district_name]

                true_winner = self.get_winner(real).party
                pred_winner = self.get_winner(prediction).party

                if self.name == 'TSS' and self.get_winner(prediction).votes == 0:
                    continue

                if pred_winner not in seats:
                    seats.setdefault(pred_winner, 0)

                if true_winner not in seats:
                    seats.setdefault(true_winner, 0)

                seats[true_winner] += 1

                y_true.append(true_winner)
                y_pred.append(pred_winner)


        label = list(seats.keys())
        label.sort()
        label.sort(key=lambda x: seats[x], reverse=True)

        return label, confusion_matrix(y_true, y_pred, labels=label)
    
    def draw_confusion_matrix(self, d_i: int):
        label, cm = self.get_confusion_matrix(d_i)
        ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=label).plot()
        plt.title(f'{self.name}: Confusion matrix for {self.dates[d_i]} election')
        plt.show()

    def draw_bar_plot(self, d_i: int, title: str):
        pass