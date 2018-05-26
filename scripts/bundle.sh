#!/bin/bash
pushd /ig/igfirehose
rm spidy.tar.gz
tar -czf spidy.tar.gz igf-py/igf.conf scrapy.cfg scrapy_instagram scripts
