=========================
SAp CTA data pipeline API
=========================

.. module:: mrif

The library provides classes which are usable by third party tools.

.. note::

    This project is still in *beta* stage, so the API is not finalized yet.

Benchmark package:

.. toctree::
   :maxdepth: 1

   mrif.benchmark.assess <api_benchmark_assess>

Denoising package:

.. toctree::
   :maxdepth: 1

   mrif.denoising.wavelets_mrfilter <api_filter_wavelet_mrfilter>
   mrif.denoising.wavelets_mrtransform <api_filter_wavelet_mrtransform>
   mrif.denoising.abstract_cleaning_algorithm <api_filter_abstract_cleaning_algorithm>
   mrif.denoising.inverse_transform_sampling <api_filter_inverse_transform_sampling>

Image package:

.. toctree::
   :maxdepth: 1

   mrif.image.hillas_parameters <api_image_hillas_parameters>
   mrif.image.pixel_clusters <api_image_pixel_clusters>
   mrif.image.signal_to_border_distance <api_image_signal_to_border_distance>

I/O package:

.. toctree::
   :maxdepth: 1

   mrif.io.geometry_converter <api_io_geometry_converter>
   mrif.io.images <api_io_images>

Optimization package:

.. toctree::
   :maxdepth: 1

   mrif.optimization.bruteforce <api_optimization_bruteforce>
   mrif.optimization.differential_evolution <api_optimization_differential_evolution>
   mrif.optimization.saes <api_optimization_saes>
   mrif.optimization.objectivefunc.wavelets_mrfilter_delta_psi <api_optimization_objectivefunc_wavelets_mrfilter_delta_psi>

