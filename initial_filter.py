#!/usr/bin/env python3

import findspark
findspark.init()
import pyspark
import regex
from contextlib import contextmanager
import time

DATA_PATH = "/home/ubuntu/data/BreachCompilation/data/*/*"


@contextmanager
def spark_context(app_name):
    sc = pyspark.SparkContext(appName=app_name,
                              master="spark://192.168.1.127:7077")
    sc.setLogLevel("ERROR")
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


if __name__ == '__main__':
    with spark_context("No Regex") as sc:
        start = time.time()
        pws = sc.textFile(DATA_PATH).cache()

        clean_pws = pws.map(extract_password) \
                       .filter(is_ascii_128) \
                       .cache()

        print("No regex count: {}, runtime: {}"
              .format(clean_pws.count(),
                      time.time() - start))
