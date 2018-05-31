import redis
import json
import sys
import argparse
import zlib
from IGFirehose import IGFirehose

parser = argparse.ArgumentParser()
parser.add_argument("-t","--tag", help="hashtag",type=str,required=True)
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

igf = IGFirehose(args.config)
print igf.get_n_mined(args.tag)
