#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016,2017,2018 Jérémie DECOCK (http://www.jdhp.org)

# This script is provided under the terms and conditions of the MIT license:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__all__ = ['benchmark']

def benchmark(benchmark_image_generator,
              processing,
              metrics,
              benchmark_writter=None,
              score_aggregation_method=None):

    score_list = []

    for benchmark_image in benchmark_image_generator:
        output_image = processing(benchmark_image.input_image)
        score = metrics(output_image, benchmark_image.reference_image)
        score_list.append(score)

        if benchmark_writter is not None:
            benchmark_writter.write(benchmark_image, score)
        else:
            print(score)

    if score_aggregation_method is not None:
        return score_aggregation_method(score_list)
    else:
        return score_list
