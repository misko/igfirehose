#!/bin/bash
pushd /tmp
rm spidy.tar.gz
wget http://igfirehose.com:59995/static/spidy.tar.gz
rm -rf /tmp/igf
mkdir /tmp/igf
tar -zxvf spidy.tar.gz -C /tmp/igf
