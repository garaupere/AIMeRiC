import os


import metronome as met
import pandas as pd
import csv


def prepare_data():
    arr = {}
    for file in os.listdir('../escansio/results'):
        if file.endswith('.csv'):
            print(file)
            data = pd.read_csv(f'../escansio/results/{file}', delimiter=';')
            print(data)
            author = data['author'][0]
            met_data = ''.join(data['metronome'])
            arr[f"{author}"] = f"{met_data}"
    dat_ready = pd.DataFrame(arr.items(), columns=['author', 'metronome'])
    dat_ready.to_csv('metronome/met.csv', index=False, encoding='utf-8', sep=';')
    print('Data prepared')


def metronome_analyze():
    df = pd.read_csv('metronome/met.csv', delimiter=';', encoding='utf-8')
    scorer = met.scoring.Scorer()
    df1 = scorer.dist_matrix(df, col='metronome')
    print(df1)
    # Advanced Scoring - Custom params for the BioPython Aligner

    # Match dict - bonus for matches, penalty for mismatches
    md = {
        ("|", "|"): 2,
        ("w", "w"): 2,
        ("S", "S"): 2,
        (".", "."): 1,
        # penalise non-alignment at line ends more, because they're rarer. The idea
        # is to stop hendecasyllables being routinely padded out to match hexameter
        # lines
        ("|", "S"): -4,
        ("|", "w"): -4,
        ("|", "."): -4,
        ("w", "S"): 0,
        ("w", "."): 0,  # not sure. In theory we don't care if spaces mismatch
        ("S", "."): 0,  # because metre isn't based on a fixed number of words
    }
    # open and extend penalties for alignment gaps
    open_penalty = -6
    extend_penalty = -3

    s = met.scoring.Scorer(match_dict=md, open_gap_score=open_penalty, extend_gap_score=extend_penalty)
    s.dist_matrix_parallel(df)
    print(s.dist_matrix_parallel(df))

if __name__ == '__main__':
    # prepare_data()
    metronome_analyze()
