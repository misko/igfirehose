import redis
import sys

from IGFirehose import IGFirehose

if len(sys.argv)!=3:
    print("%s config tag" % sys.argv[0])
    sys.exit(1)

config_fn = sys.argv[1]
tag=sys.argv[2].strip()

igf = IGFirehose(config_fn)
if len(tag)==0:
    sys.exit(1)
igf.add_auto_tag(tag)
