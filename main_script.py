#!/usr/bin/env python3
import time
import re
from contextlib import contextmanager
import findspark
import argparse
findspark.init()
import pyspark
from pyspark.sql.types import Row

NFS_DATA_PATH = "/home/ubuntu/data/BreachCompilation/data/*/*"
HDFS_DATA_PATH = "hdfs://namenode:9000/user/ubuntu/BreachCompilation/data/*/*"
SAVE_PATH = "/home/ubuntu/data/BreachCompilation/"
SPARK_MASTER = "spark://group-2-project-1:7077"
RUNTIME_DATA_FILE = "/home/ubuntu/runtimes"

# # # We consider ASCII-128 characters and symbols only..
DIGITS = list('0123456789')
ALPHAS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
SPECIALS = list(' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
PATTERN = r'[0-9]+|[a-zA-Z]+|[ !"#$%&\'()*+,-./:;<=>?@\[\]\^_`{\|}~\\\\]+'


@contextmanager
def spark_context(app_name):
    sc = pyspark.SparkContext(appName=app_name, master=SPARK_MASTER)
    sc.setLogLevel("WARN")
    yield sc
    sc.stop()


def extract_password(uname_pwd):
    """
    Extract the password of a colon-separated list. Return None if the
    list was somehow invalid.

    """
    try:
        return uname_pwd.split(":")[1]
    except IndexError:
        return None


def is_ascii_128(password):
    # Filter Null values or empty strings:
    if not password or not password.strip():
        return False
    try:
        password.encode().decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def get_base_structure_format(word, string_len=True):
    """
    Function converts a password to its base structures as defined by the Weir cracking algorithm using their
    definition of L (for alpha strings), D (for digits strings) and S (for special character strings).

    Args:
        word (String): password input to analyse.
        string_len (Bool): whether to return info about the base structure length.

    Returns:
        String: denoting the base structures style.

    Notes:
        Uses nonlocal variables defined at module level. In spark context possibly use broadcast vars or supply args?

    Doctests:
    >>> get_base_structure_format('Password123$')
    '-L8-D3-S1-'
    >>> get_base_structure_format('$1Password1$')
    '-S1-D1-L8-D1-S1-'
    >>> get_base_structure_format('Password123$', string_len=False)
    '-L-D-S-'
    >>> get_base_structure_format('$1Password1$', string_len=False)
    '-S-D-L-D-S-'
    >>> get_base_structure_format('Password123 !"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'+"'" , string_len=False)
    '-L-D-S-'
    """
    structures = re.findall(PATTERN, word)
    base = '-'
    for structure in structures:
        if structure[0] in ALPHAS:
            # then this is an alpha string structure
            base += 'L'
        elif structure[0] in DIGITS:
            # then this is a digit structure
            base += 'D'
        else:
            # the final, least likely outcome is a special structure
            base += 'S'

        if string_len:
            base += str(len(structure)) + '-'
        else:
            base += '-'

    return base


def get_base_structures(word_count, use_count=True):
    """
    Function operates with RDD input and returns a generator of extended output to be flatMapped.

    Args:
        word_count (tuple): key-value pair of RDD input containing a password and associated count.
        use_count (bool): whether to include the information about associated count

    Returns:
        generator: of ordered base structures detected in word with associated counts if required.

    Notes:
        Uses nonlocal variables defined at module level. In spark context possibly use broadcast vars or supply args?

    Doctests:
    >>> g = get_base_structures(('password123re', 1000))
    >>> next(g)
    ('password', 1000)
    >>> next(g)
    ('123', 1000)
    >>> next(g)
    ('re', 1000)

    >>> g = get_base_structures(('qwerty9', 1000), use_count=False)
    >>> next(g)
    ('qwerty', 1)
    >>> next(g)
    ('9', 1)

    >>> g = get_base_structures(('Password123 !"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'+"'", 999))
    >>> next(g)
    ('Password', 999)
    >>> next(g)
    ('123', 999)
    >>> next(g)
    (' !"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\'', 999)
    """
    structures = re.findall(PATTERN, word_count[0])

    if use_count:
        count = word_count[1]
    else:
        count = 1

    for structure in structures:
        yield (structure, count)


def structure_filter(structure, s_type):
    """
    Filters structures for the specific types: alpha, digit or special.

    Args:
        structure (string): inpiut structure to parse
        stype (string): parsing parameter accepting 'alpha', 'digit', 'special'.

    Returns
        Bool: whether condition is satisfied by structure

    Doctests:
    >>> structure_filter('Password', type='alpha')
    True
    >>> structure_filter('Password', type='digit')
    False
    """
    if structure[0] in ALPHAS:
        # then this is an alpha string structure
        return s_type == 'alpha'
    elif structure[0] in DIGITS:
        # then this is a digit structure
        return s_type == 'digit'
    else:
        # the final, least likely outcome is a special structure
        return s_type == 'special'

# EXCLUDED FOR INCOMPATIBILITY WITH SPARK API TYPE
#
# def df_rows(w, *args):
#     """
#     Utility function for dynamically creating dataframes from RDDs in combination with pyspark Row()
#
#     Args:
#         w (tuple): RDD element
#         *args (string): names for the associated dict keys to which RDD data is assigned. Must be length same as w.
#
#     Retuns:
#         Dict: assigning the data from element w to the dict keys
#
#     Doctests:
#     >>> df_rows(('some_data', 1000), *('Name', 'Count'))
#     {'Name': 'some_data', 'Count': 1000}
#     """
#     d = dict()
#     for i in range(len(w)):
#         d[args[i]] = w[i]
#     return d
#
#
# def convert_toDF(rdd, *args):
#     """
#     Utility function to return a DF from an RDD using pyspark Row()
#
#     Args:
#         rdd (RDD): ...
#         *args (strings): defining column headers of each RDD row element data, must be length of RDD row data.
#
#     Returns:
#         DF: a dataframe with column elements named according to args
#     """
#     df = rdd.map(lambda w: Row(**df_rows(w, *args))).toDF()
#
#
# def write_toCSV(df, filename):
#     """
#     Utility function to write a spark DF to a CSV, with default options
#
#     Args:
#         df (DF): ...
#         filename: to save to, will create a directory if multiple files.
#
#     Returns:
#         None
#     """
#     df.write \
#       .option("header", "true") \
#       .option('quote', '"') \
#       .option('escape', '"') \
#       .option('delimiter', ',') \
#       .csv(filename)
#     return None


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description="Parse password dump")
    argument_parser.add_argument('--storage-backend',
                                 help="Use HDFS or NFS?",
                                 type=str,
                                 choices=["hdfs", "nfs"],
                                 default="hdfs")

    argument_parser.add_argument('worker_count',
                                 help=("The number of Spark workers we are using, "
                                       "for statistics."),
                                 type=int)

    argument_parser.add_argument('--save-results',
                                 help="Dump the results to CSV",
                                 action='store_true')


    args = argument_parser.parse_args()
    if args.storage_backend == "hdfs":
        data_path = HDFS_DATA_PATH
    else:
        data_path = NFS_DATA_PATH

    with spark_context("No Regex") as sc:
        start = time.time()
        suffix = str(int(start))

        # # # 1) read the raw files and process into a password-count RDD which persists in Cache
        rdd_pwd_cnt = sc.textFile(data_path) \
                        .map(extract_password) \
                        .filter(is_ascii_128) \
                        .map(lambda w: (w, 1)) \
                        .reduceByKey(lambda tot, v: tot + v) \
                        .cache()
        # rdd_pwd_cnt has the format [ ('password', 999), ('qwerty', 1000), .. ]

        # # # 2) perform analysis evaluating the generic base structures without count
        rdd_base_struc_form = rdd_pwd_cnt.map(lambda w: (get_base_structure_format(w[0], string_len=False), 1)) \
                                         .reduceByKey(lambda tot, v: tot + v) \
                                         .map(lambda w: (w[1], w[0])) \
                                         .sortByKey(ascending=False)
        # rdd_base_struc_form has the format [ (1000, '-L-D-'), (999, '-L-'), .. ]
        print('Our analysis of base structure (without duplicates) show the following most frequently occurring.. ')
        for k in rdd_base_struc_form.take(100):
            print('{}: {}'.format(k[1], k[0]))

        if args.save_results:
            rdd_base_struc_form.map(lambda w: w[1] + ',' + str(w[0]))\
                               .saveAsTextFile(SAVE_PATH + "rdd_base_struc_form_"+ suffix)


        # # # 3) perform analysis evaluating the generic base structures with count
        rdd_base_struc_form_cnt = rdd_pwd_cnt.map(lambda w: (get_base_structure_format(w[0], string_len=False), w[1])) \
                                             .reduceByKey(lambda tot, v: tot + v) \
                                             .map(lambda w: (w[1], w[0])) \
                                             .sortByKey(ascending=False)
        # rdd_base_struc_form_cnt has the same format as above with expected larger counts.
        print('Our analysis of base structure (with duplicates) show the following most frequently occurring.. ')
        for k in rdd_base_struc_form_cnt.take(100):
            print('{}: {}'.format(k[1], k[0]))

        if args.save_results:
            rdd_base_struc_form_cnt.map(lambda w: w[1] + ',' + str(w[0]))\
                                   .saveAsTextFile(SAVE_PATH + "rdd_base_struc_form_cnt_"
                                                   + suffix)

        # # # 4) perform analysis getting the actual alpha, digit and special strings and performing reduced count
        rdd_base_struc_data = rdd_pwd_cnt.flatMap(lambda w: get_base_structures(w, use_count=True)) \
                                         .reduceByKey(lambda tot, v: tot + v) \
                                         .cache()

        # # # 5) filter the data to display some interesting results, take the top 100 base structures in each category
        for s_type in ['alpha', 'digit', 'special']:
            print('We determine the following most frequently occurring {} strings..'.format(s_type))
            rdd_filter = rdd_base_struc_data.filter(lambda w: structure_filter(w[0], s_type=s_type)) \
                                            .map(lambda w: (w[1], w[0]))\
                                            .sortByKey(ascending=False)\
                                            .cache()
            for k in rdd_filter.take(100):
                print('{}: {}'.format(k[1], k[0]))

            if args.save_results:
                rdd_filter.map(lambda w: w[1] + ',' + str(w[0]))\
                          .saveAsTextFile(SAVE_PATH + "rdd_{}_".format(s_type) + suffix)

        # # # 6) Return procedure stats
        result_time = time.time() - start
        print("Complete. Runtime: {}".format(result_time))
        with open("{}.{}".format(RUNTIME_DATA_FILE,
                                 args.storage_backend), "a") as fp:
            fp.write("{};{};{};{}\n".format(start,
                                            time.time(),
                                            args.worker_count,
                                            result_time))
