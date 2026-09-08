* ISO3_GCAM now covers all GCAM versions from 4.0 to 9.1, plus the GCAM 3 regions
  as ``GCAM 3.0|*``.
* The GCAM regions are now generated from the mapping files in the ``gcam-core``
  repository, which are the definitions GCAM itself runs on, instead of from the
  rendered GCAM documentation. As a consequence, the regions now also contain
  dependent territories which the documentation omits, for example Hong Kong and
  Macao in ``China`` or Puerto Rico in ``USA``.
* GCAM versions which define their regions identically are now a single category with
  the other versions as alternative codes, so that for example
  ``ISO3_GCAM["GCAM 9.1|USA"] == ISO3_GCAM["GCAM 8.1|USA"]``.
* Kosovo was added to ISO3_GCAM as ``XKX`` because GCAM 7.4 and later use it. It is not
  part of ISO 3166-1 and therefore not part of ISO3.
* Regions which are spelled differently in different places are now available under
  both spellings, i.e. ``Australia_NZ`` and ``Australia and New Zealand`` as well as
  ``Central America and Caribbean`` and ``Central America and the Caribbean``.
* Fixed the ``GCAM 8s|*`` codes. They now refer to the regions of GCAM
  7.4 and 8.0, matching the CMIP7 runs labelled "GCAM 8s", instead of to the regions of
  GCAM 8.1 and later. Note that this renames ``GCAM 8s|Ukraine`` to
  ``GCAM 8s|Europe_Eastern``, which is how GCAM 8.0 calls that region.
