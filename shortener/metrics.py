""" stub code for metrics/reporting """
import sys

def log_redirect(short_key):
    print("REDIRECT: {}".format(short_key), file=sys.stderr)

def log_creation(short_key, long_url):
    print("CREATED: {} for {}".format(short_key, long_url), file=sys.stderr)
