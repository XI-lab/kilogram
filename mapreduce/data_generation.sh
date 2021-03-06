#!/usr/bin/env bash
cd /tmp
git clone https://github.com/dragoon/kilogram.git
cd kilogram/mapreduce


wget http://downloads.dbpedia.org/2015-04/dbpedia_2015-04.owl.bz2
wget http://downloads.dbpedia.org/2015-04/core/disambiguations_en.nt.bz2
wget -O redirects_transitive_en.nt.bz2 http://downloads.dbpedia.org/2015-04/core-i18n/en/transitive-redirects_en.nt.bz2

# types
wget http://downloads.dbpedia.org/2015-04/core-i18n/en/instance_types_sdtyped-dbo_en.nt.bz2
wget http://downloads.dbpedia.org/2015-04/core-i18n/en/instance-types-transitive_en.nt.bz2
wget http://downloads.dbpedia.org/2015-04/core-i18n/en/instance-types_en.nt.bz2

# dbpedia_data generation
python dbpedia_dbp.py


# wiki_urls and wiki_achors generation
hdfs dfs -rm -r /user/roman/wiki_anchors /user/roman/wiki_urls
spark-submit --executor-memory 5g --num-executors 10 --master yarn-client ./wikipedia/spark_anchors.py "/user/ded/link_mention" "/user/roman/wiki_anchors" "/user/roman/wiki_urls"
echo "disable 'wiki_anchors'" | hbase shell -n
echo "drop 'wiki_anchors'" | hbase shell -n
echo "create 'wiki_anchors', 'ngram'" | hbase shell -n
pig -p table=wiki_anchors -p path=/user/roman/wiki_anchors ../extra/hbase_upload_array.pig
echo "disable 'wiki_urls'" | hbase shell -n
echo "drop 'wiki_urls'" | hbase shell -n
echo "create 'wiki_urls', 'ngram'" | hbase shell -n
pig -p table=wiki_urls -p path=/user/roman/wiki_urls ../extra/hbase_upload_array.pig

# candidate_ngrams generation - depends on prev task
hdfs dfs -rm -r /user/roman/SOTA_EL/candidate_ngram_links
spark-submit --master yarn-client --num-executors 10 --executor-memory 5g ./entity_linking/spark_candidate_ngrams.py "/user/roman/dbpedia_data.txt" "/user/roman/wiki_anchors" "/user/roman/SOTA_EL/candidate_ngram_links"
echo "disable 'wiki_anchor_ngrams'" | hbase shell -n
echo "drop 'wiki_anchor_ngrams'" | hbase shell -n
echo "create 'wiki_anchor_ngrams', 'ngram'" | hbase shell -n
pig -p table=wiki_anchor_ngrams -p path=/user/roman/SOTA_EL/candidate_ngram_links ../extra/hbase_upload_array.pig


# wiki direct links table
spark-submit --master yarn-client --executor-memory 5g --num-executors 10 ./entity_linking/spark_wikilinks.py "/user/ded/TL" "/user/roman/SOTA_EL/TL_processed"
echo "disable 'TL'" | hbase shell -n
echo "drop 'TL'" | hbase shell -n
echo "create 'TL', 'ngram'" | hbase shell -n
pig -p table=TL -p path=/user/roman/SOTA_EL/TL_processed ../extra/hbase_upload_array.pig

spark-submit --master yarn-client --executor-memory 5g --num-executors 10 ./entity_linking/spark_wikilinks.py "/user/ded/LL" "/user/roman/SOTA_EL/LL_processed"
echo "disable 'LL'" | hbase shell -n
echo "drop 'LL'" | hbase shell -n
echo "create 'LL', 'ngram'" | hbase shell -n
pig -p table=LL -p path=/user/roman/SOTA_EL/LL_processed ../extra/hbase_upload_array.pig


spark-submit --master yarn-client --executor-memory 5g --num-executors 10 ./entity_linking/spark_wikilinks_mentions.py "/user/ded/CC" "/user/roman/SOTA_EL/CC_processed"
echo "disable 'CC'" | hbase shell -n
echo "drop 'CC'" | hbase shell -n
echo "create 'CC', 'ngram'" | hbase shell -n
pig -p table=CC -p path=/user/roman/SOTA_EL/CC_processed ../extra/hbase_upload_array.pig


# lowercased anchors
hdfs dfs -rm -r /user/roman/SOTA_EL/candidate_ngram_links_nospace
spark-submit --master yarn-client --num-executors 10 --executor-memory 5g ./entity_linking/spark_candidate_ngrams.py --nospace "/user/roman/dbpedia_data.txt" "/user/roman/wiki_anchors" "/user/roman/SOTA_EL/candidate_ngram_links_nospace"
echo "disable 'wiki_anchor_ngrams_nospace'" | hbase shell -n
echo "drop 'wiki_anchor_ngrams_nospace'" | hbase shell -n
echo "create 'wiki_anchor_ngrams_nospace', 'ngram'" | hbase shell -n
pig -p table=wiki_anchor_ngrams_nospace -p path=/user/roman/SOTA_EL/candidate_ngram_links_nospace ../extra/hbase_upload_array.pig