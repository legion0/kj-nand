#!/bin/bash

EX=3
TAR_FILE=project$EX.tar
FILE_LIST='1/Bit  1/PC  1/RAM64  1/RAM8  1/Register  2/RAM16K  2/RAM4K  2/RAM512'

mkdir testTar
cp $TAR_FILE testTar/
cd testTar/
temp=`pwd`

tar -xf $TAR_FILE

for CHIP in $FILE_LIST; do
  if [ ! -r $CHIP.hdl ]; then
    CHIP=`echo $CHIP | sed 's/1\//a\//'`
    CHIP=`echo $CHIP | sed 's/2\//b\//'`
    if [ ! -r $CHIP.hdl ]; then
       D=`echo $CHIP | sed 's/a.*/1 or a/'`
       D=`echo $D | sed 's/b.*/2 or b/'`
       CHIP=`echo $CHIP | sed 's/\(1\/\)|\(2\/\)|\(a\/\)|\(b\/\)//'`
       echo Chip $CHIP was not found in directory $D
    fi
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