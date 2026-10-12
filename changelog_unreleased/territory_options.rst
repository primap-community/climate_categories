* Added options for territories to ``ISO3``: ``territories_in_sovereign_inventory``
  includes dependent territories in their sovereign country if the national greenhouse
  gas inventory of the sovereign country under the UNFCCC covers them, like Greenland
  (``GRL``) in Denmark (``DNK``). ``no_unpopulated`` removes territories without permanent
  population, like Antarctica (``ATA``). ``antilles`` includes Curaçao, Sint Maarten, and
  Bonaire, Sint Eustatius and Saba in the Netherlands Antilles (``ANT``), which then
  is part of ``World``. ``esh_in_mar`` includes Western Sahara (``ESH``) in Morocco
  (``MAR``). ``msr_pcn_in_gbr`` includes Montserrat and Pitcairn, which are not
  covered by the inventory of the United Kingdom, but have a tiny population, in the
  United Kingdom (``GBR``). The options ``territories_in_sovereign_inventory``,
  ``antilles``, and ``msr_pcn_in_gbr`` are not supported together with ``gcam``.
