#!/bin/bash

pushd /tmp/igf

while [ 1 -lt 2 ]; do
         scrapy crawl -a config_fn=/tmp/igf/igf-py/igf.conf hashtag
         sleep 30
done
