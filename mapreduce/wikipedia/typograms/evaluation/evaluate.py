from __future__ import division
from __future__ import print_function
import argparse
from functools import partial
import os
import re
from .link_generators import generate_organic_links, generate_links, unambig_generator,\
    label_generator,  generate_organic_plus, generate_organic_precise_plus

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--gold-file', required=True,
                    help='path to the file with the ground truth')
parser.add_argument('--eval-dir', required=True,
                    help='path to the directory to evaluate')
parser.add_argument('--out-file', default="not_ranked.txt",
                    help='path to the file to output non-ranked items')

args = parser.parse_args()

SENT_STRIP_RE = re.compile(r'[\"\'\s]')


def get_unambiguous_labels(filename):
    unambiguous_labels = {}
    for line in open(filename, 'r'):
        label, uri = line.strip().split('\t')
        unambiguous_labels[label] = uri
    return unambiguous_labels


def get_gold_data():
    gold_data = {}
    for line in open(args.gold_file):
        correct, uri_equals, full_url, token, uri, orig_sentence = line.strip().split('\t')
        token = SENT_STRIP_RE.sub("", token.replace("'s", ""))
        sentence = SENT_STRIP_RE.sub("", orig_sentence)
        gold_data[(token, uri, sentence)] = int(correct)
    return gold_data

gold_data = get_gold_data()
not_ranked_data = set()


def evaluate(eval_name, evaluator, eval_dir):
    """
    :param eval_name: name of the evaluator, can be anything
    :param evaluator: evaluator function (see examples)
    :return: precision
    """
    labels = []
    print('Evaluating:', eval_name)
    for filename in os.listdir(eval_dir):
        for line in open(eval_dir + '/' + filename):
            for token, uri, orig_sentence in evaluator(line):
                sentence = SENT_STRIP_RE.sub("", orig_sentence)
                token = SENT_STRIP_RE.sub("", token.replace("'s", ""))
                if (token, uri, sentence) in gold_data:
                    label = gold_data[(token, uri, sentence)]
                    labels.append(label)
                else:
                    not_ranked_data.add((token, uri, orig_sentence))
    print('Precision:', sum(labels)/len(labels))
    print('Recall:', sum(labels)/total_correct)
    print('.')
    return sum(labels)/len(labels)


total_correct = sum(gold_data.values())



print('Evaluating parameters...')



print('Evaluating unambiguous labels by ratios...')
for filename in os.listdir('.'):

    # unambiguous labels generated by various ratios
    if filename.startswith('unambiguous_labels'):
        unambiguous_labels = get_unambiguous_labels(filename)
        unambig_generator = partial(unambig_generator, unambiguous_labels=unambiguous_labels)
        evaluate('inferred-labels ' + filename,  partial(generate_links, generators=[unambig_generator]), args.eval_dir)
        evaluate('inferred + organic-precise ' + filename,
                 partial(generate_organic_precise_plus, evaluator=partial(generate_links, generators=[unambig_generator])), args.eval_dir)
        evaluate('inferred + organic ' + filename,
                 partial(generate_organic_plus, evaluator=partial(generate_links, generators=[unambig_generator])), args.eval_dir)
        evaluate('inferred + all-dbpedia-labels ' + filename,
                 partial(generate_links, generators=[unambig_generator, label_generator]), args.eval_dir)
        evaluate('inferred + all-dbpedia-labels + organic-precise ' + filename,
                 partial(generate_organic_precise_plus, evaluator=partial(generate_links, generators=[unambig_generator, label_generator])), args.eval_dir)

print('Evaluating unambiguous labels by percentiles...')
percentile_dir = 'unambig_percentile'
for filename in os.listdir(percentile_dir):
    # unambiguous labels generated by percentile of counts
    if 'ratio' in filename:
        print('Evaluating ' + filename)
        unambiguous_labels = get_unambiguous_labels(percentile_dir + '/' + filename)
        unambig_generator = partial(unambig_generator, unambiguous_labels=unambiguous_labels)
        evaluate('inferred-percentile ' + filename,  partial(generate_links, generators=[unambig_generator]), args.eval_dir)


print('Evaluating organic...')

evaluations = [('organic', generate_organic_links),
               ('organic-precise', generate_organic_precise_plus),
               ('all-dbpedia-labels', partial(generate_links, generators=[label_generator]))
               ]


for eval_name, evaluator in evaluations:
    evaluate(eval_name, evaluator, args.eval_dir)

# evaluate spotlight
for spot_dir in os.listdir('./spotlight'):
    evaluate('spotlight-' + spot_dir, generate_organic_links, './spotlight/' + spot_dir)


not_ranked_file = open(args.out_file, 'w')
for values in not_ranked_data:
    not_ranked_file.write('\t'.join(values)+'\n')
not_ranked_file.close()
