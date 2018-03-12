=========================
SAp CTA data pipeline API
=========================

.. module:: pywi

The library provides classes which are usable by third party tools.

.. note::

    This project is still in *beta* stage, so the API is not finalized yet.

Benchmark package:

.. toctree::
   :maxdepth: 1

   pywi.benchmark.assess <api_benchmark_assess>

Denoising package:

.. toctree::
   :maxdepth: 1

   pywi.denoising.wavelets_mrfilter <api_filter_wavelet_mrfilter>
   pywi.denoising.wavelets_mrtransform <api_filter_wavelet_mrtransform>
   pywi.denoising.abstract_cleaning_algorithm <api_filter_abstract_cleaning_algorithm>

Image package:

.. toctree::
   :maxdepth: 1

   pywi.image.pixel_clusters <api_image_pixel_clusters>

I/O package:

.. toctree::
   :maxdepth: 1

   pywi.io.images <api_io_images>

Optimization package:

.. toctree::
   :maxdepth: 1

   pywi.optimization.bruteforce <api_optimization_bruteforce>
   pywi.optimization.differential_evolution <api_optimization_differential_evolution>
   pywi.optimization.saes <api_optimization_saes>
   pywi.optimization.objectivefunc.wavelets_mrfilter_delta_psi <api_optimization_objectivefunc_wavelets_mrfilter_delta_psi>

