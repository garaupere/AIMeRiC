import os

import metronome as met
import pandas as pd
import csv

from AIMeRiC.corpus.modules.getUSB import getUSB


def prepare_data(corpus):
    arr = {}
    usb = getUSB()
    data = pd.read_csv(f'{usb}/corpora/{corpus}/etiquetat/{corpus}.csv', delimiter=';')
    # Conservar només les columnes que ens interessen (autor i metronome)
    data = data[['metronome', 'autor']]
    return data


def metronome_analyze(data):
    scorer = met.scoring.Scorer()
    df1 = scorer.dist_matrix(data, col='metronome')
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
    s.dist_matrix_parallel(data)
    print(s.dist_matrix_parallel(data))


if __name__ == '__main__':
    data = prepare_data('__test')
    metronome_analyze(data)
