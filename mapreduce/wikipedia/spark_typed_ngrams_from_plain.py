"""
spark-submit --num-executors 20 --executor-memory 7g --master yarn-client --files "/home/roman/dbpedia/dbpedia_types.txt,/home/roman/dbpedia/dbpedia_uri_excludes.txt,/home/roman/dbpedia/dbpedia_lower_includes.txt,/home/roman/dbpedia/dbpedia_redirects.txt,/home/roman/dbpedia/dbpedia_2015-04.owl" ./wikipedia/spark_typed_ngrams_from_plain.py "/user/roman/wikipedia_ngrams" "/user/roman/wikipedia_typed_ngrams" 3
"""
import sys
from pyspark import SparkContext
from kilogram.dataset.dbpedia import NgramEntityResolver

sc = SparkContext(appName="SparkGenerateTypedNgramsFromPlain")

N = int(sys.argv[3])

ngram_lines = sc.textFile(sys.argv[1])

ner = NgramEntityResolver("dbpedia_types.txt", "dbpedia_uri_excludes.txt",
                          "dbpedia_lower_includes.txt", "dbpedia_redirects.txt",
                          "dbpedia_2015-04.owl")

def map_types(line):
    ngram, count = line.strip().split('\t')
    return ' '.join(ner.replace_types(ner.resolve_entities(ngram.split()), order=-1)), int(count)

typed_ngrams = ngram_lines.map(map_types).filter(lambda x: '<dbpedia:' in x[0] and len(x[0].split()) <= N)
#typed_ngrams = typed_ngrams.reduceByKey(lambda n1, n2: n1+n2)

typed_ngrams.map(lambda x: x[0]+'\t'+str(x[1])).saveAsTextFile(sys.argv[2])