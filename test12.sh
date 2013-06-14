#!/bin/bash

EX=12
TAR_FILE=project$EX.tar
FILE_LIST='Array Keyboard Math Memory Output Screen String Sys'

rm -fr testTar
mkdir testTar
cp $TAR_FILE testTar/
cd testTar/
tar -xf $TAR_FILE

for OS in $FILE_LIST; do
  if [ ! -r $OS.jack ]; then
      echo $OS was missing
  fi
done


if [ -r README ]; then
  dos2unix README &> /dev/null
  logins=`head -1 README`
  echo Your logins are: $logins, is that ok?
else
  echo No README was found
fi

cd ../
rm -Rf testTar