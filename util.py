class Candidate:
    def __init__(self, party: str, name: str, votes: float):
        self.party = party
        self.name = name
        self.votes = votes

    def __str__(self):
        return str((self.party, self.name, self.votes))