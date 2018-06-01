#!/bin/bash
pushd /tmp
rm spidy.tar.gz
cp /ig/igfirehose/spidy.tar.gz ./
rm -rf /tmp/igf
mkdir /tmp/igf
tar -zxvf spidy.tar.gz -C /tmp/igf
