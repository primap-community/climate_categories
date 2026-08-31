* Removed the unused ``numpy`` dependency. ``climate_categories`` never imported numpy;
  the version pins only existed to push a NEP 29-compliant numpy onto users, which
  ``pandas >= 3.0`` already does. This also fixes the pins having fallen below the NEP 29
  floor, which moved to numpy 2.2 on 2026-08-19.
