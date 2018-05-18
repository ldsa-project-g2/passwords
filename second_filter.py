#!/usr/bin/env python3

import findspark
findspark.init()
import pyspark
import re
from operator import add
from contextlib import contextmanager
import time

DATA_PATH = ""  # <- NEEDS MAP-REDUCED FILE OF STAGE ONE FILTERING
"""
File structure for this analysis should be of the format, <string><tab><count>:

password\t10010
qwerty\t9999
banana\t8007
...

"""

# # # We consider ASCII-128 characters and symbols only..
DIGITS = list('0123456789')
ALPHAS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
SPECIALS = list(' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

USE_COUNT = True


@contextmanager
def spark_context(app_name):
    sc = pyspark.SparkContext(appName=app_name,
                              master="spark://192.168.1.127:7077")
    sc.setLogLevel("ERROR")
    yield sc
    sc.stop()


def get_password_count_pair(line):
    """
    Reads the map reduced password-count file and returns a datapoint as a tuple containing (password, count)

    Args:
        line (str): a line from the previously map reduced program, tab separated.

    Returns:
        tuple: (String of password, Int of password count)

    Doctests:
    >>> get_password_count_pair('password\t10000')
    ('password', 10000)

    """
    s = line.split('\t')
    return s[0], int(s[1])


def get_base_structure_format(word):
    """
    Function converts a password to its base structures as defined by the Weir cracking algorithm using their
    definition of L (for alpha strings), D (for digits strings) and S (for special character strings).

    Args:
        word (String): password input to analyse

    Returns:
        String: denoting the base structure style

    Notes:
        Uses nonlocal variables defined at module level. In spark context possibly use broadcast vars or supply args?

    Doctests:
    >>> get_base_structure_format('Password123$')
    '-L8-D3-S1-'
    >>> get_base_structure_format('$1Password1$')
    '-S1-D1-L8-D1-S1-'

    """
    structures = re.findall(r'[0-9]+|[a-zA-Z]+|[' + ''.join(SPECIALS) + r']+', word)
    base = '-'
    for structure in structures:
        if structure[0] in ALPHAS:
            # then this is an alpha string structure
            base += 'L' + str(len(structure)) + '-'
        elif structure[0] in DIGITS:
            # then this is a digit structure
            base += 'D' + str(len(structure)) + '-'
        else:
            # the final, least likely outcome is a special structure
            base += 'S' + str(len(structure)) + '-'
    return base


def apply_count(count):
    if USE_COUNT:
        return count
    return 1
    
# def get_base_structures(word):
#     """
#     Function converts a password to its base structures as defined by the Weir cracking algorithm using their
#     definition of L (for alpha strings), D (for digits strings) and S (for special character strings).
#
#     Args:
#         word (str): input password to analyse the structure of
#
#     Returns:
#         generator: of ordered base structures detected in word
#
#     Notes:
#         Uses nonlocal variables defined at module level. In spark context possibly use broadcast vars or supply args?
#
#
#     """


if __name__ == '__main__':
    with spark_context("No Regex") as sc:
        start = time.time()
        pws2 = sc.textFile(DATA_PATH).cache()  # <- perhaps instead of saving and loading a new file, could
                                               #    reference the first RDD created in the pipeline?

        structure_pws = pws2.map(get_password_count_pair) \
                            .map(lambda x: (get_base_structure_format(x[0]), apply_count(x[1]))) \
                            .reduceByKey(add) \
                            .cache()

        print("First few samples: {}, runtime: {}"
              .format(structure_pws.take(5),
                      time.time() - start))
