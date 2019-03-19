import redis
import json
import sys
import argparse

from IGFirehose import IGFirehose

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="config file",required=True,type=str)
args = parser.parse_args()

igf = IGFirehose(args.config)
tags=list(igf.get_mined_tags())
tags.sort()
for tag in tags:
	print(tag)
