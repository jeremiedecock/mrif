#!/bin/bash

# An iSAP/Sparse2D automated compilation and installation script for Linux.
#
# Source:
# https://github.com/tino-michael/tino_cta/blob/master/grid/compile_mrfilter_pilot.sh
# 
# Author: Tino Michael (https://github.com/tino-michael)

echo "pwd:"
pwd

echo "ls -lh"
ls -lh

# setting some paths
export PATH=./:$PATH
export LD_LIBRARY_PATH=./:$LD_LIBRARY_PATH


echo '$PATH'
echo $PATH
echo '$LD_LIBRARY_PATH'
echo $LD_LIBRARY_PATH
echo '$PYTHONPATH'
echo $PYTHONPATH


# prevent matplotlib to complain about missing backends
export MPLBACKEND=Agg

MYHOME=$PWD

export COMPILE_CFITSIO=1
export COMPILE_SPARSE=1

# getting and compiling cfitsio on site
if [ $COMPILE_CFITSIO ]  # this won't run unless we define the variable
then
    if [ ! -e cfitsio_latest.tar.gz ]
    then
        echo getting cfitsio
        wget http://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio_latest.tar.gz \
        &> /dev/null
    else
        echo cfitsio tarball already here
    fi
    tar -xzvf cfitsio_latest.tar.gz
    cd cfitsio
    ./configure
    make
    make install

    export CFITSIO=$PWD
    export LD_LIBRARY_PATH=$CFITSIO:$LD_LIBRARY_PATH

    cd $MYHOME
fi

# get and compile mr_filter
if [ $COMPILE_SPARSE ]  # this won't run unless we define the variable
then
    if [ ! -e ISAP*tgz ]
    then
        echo getting ISAP
        wget http://www.cosmostat.org/wp-content/uploads/2014/12/ISAP_V3.1.tgz \
        &> /dev/null
    else
        echo ISAP tarball already here
    fi
    tar -xzf ISAP_V3.1.tgz
    export ISAP=$PWD/ISAP_V3.1

    cd $ISAP/cxx

    echo
    echo Line ${LINENO}
    pwd
    ls

    # sparse2d looks in extern/cfitsio for libraries and headers
    # add the directories and link to cfitsio
    mkdir -p extern/cfitsio
    ln -s $CFITSIO $PWD/extern/cfitsio/include
    ln -s $CFITSIO/libcfitsio.a $PWD/extern/cfitsio

    tar -xzf sparse2d_V1.1.tgz
    cd sparse2d

    ./configure
    make

    cd $MYHOME
    cp $ISAP/cxx/sparse2d/bin/mr_filter $MYHOME
fi



echo
echo "final ls -lh"
ls -lh
