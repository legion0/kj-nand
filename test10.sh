#!/bin/bash

EX=10
TAR_FILE=project$EX.tar

rm -fr testTar
mkdir testTar
cp $TAR_FILE testTar/
cd testTar/

tar -xf $TAR_FILE
if [ ! -r Makefile ]; then
  echo Makefile was not found
  cd ../
  rm -Rf testTar
  exit 1
fi

make >& /dev/null
if [ $? -ne 0 ]; then
  echo "Make failed"
  cd ../
  rm -Rf testTar
  exit 1
fi

if [ ! -r JackAnalyzer ]; then
  echo JackAnalyzer was not found
fi

if [ -r README ]; then
  dos2unix README &> /dev/null
  logins=`head -1 README`
  echo Your logins are: $logins, is that ok?
else
  echo No README was found
fi

cd ../
rm -Rf testTar