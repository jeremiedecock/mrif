#!/bin/sh

# DOCTESTS ####################################################################

echo
echo
python3 -m doctest ./pywi/io/images.py
if [ $? -ne 0 ]; then
    exit 1
fi

# UNITTESTS ###################################################################

echo
echo
echo "TEST_BENCHMARK_ASSESS"
./tests/test_benchmark_assess.py
if [ $? -ne 0 ]; then
    exit 1
fi

#echo
#echo
#echo "TEST_KILL_ISOLATED_PIXELS"
#./tests/test_image_kill_isolated_pixels.py
#if [ $? -ne 0 ]; then
#    exit 1
#fi
#
#echo
#echo
#echo "TEST_IO_IMAGES"
#./tests/test_io_images.py
#if [ $? -ne 0 ]; then
#    exit 1
#fi
