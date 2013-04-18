#!/bin/bash

EX=1
TAR_FILE=project$EX.tar
FILE_LIST='And DMux DMux8Way Mux16 Mux8Way16 Not16 Or16 Xor And16 DMux4Way Mux Mux4Way16 Not Or Or8Way'

mkdir testTar
cp $TAR_FILE testTar/
cd testTar/
temp=`pwd`

tar -xf $TAR_FILE

for CHIP in $FILE_LIST; do
  if [ ! -r $CHIP.hdl ]; then
    echo Chip $CHIP was not found
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