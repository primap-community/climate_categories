* ISO3: Added the parties to the Paris Agreement as ``PARIS``, which always refers to
  the current parties. For every month in which parties joined or left
  the Paris Agreement, there is a category ``PARIS_YYYY_MM`` containing the parties
  after all changes in that month took effect, based on the dates on which the
  Agreement entered into force for a party or its withdrawal took effect. The comments
  give the exact period during which each category describes the parties. The last
  category of every year is also available as ``PARIS_YYYY``, so that for example
  ``ISO3["PARIS_2020"]`` gives the parties after Angola joined on 2020-12-16, without
  the USA, whose first withdrawal took effect on 2020-11-04. Only changes which took
  effect before the data was last updated are included, and codes for the current
  month and year are left out, so that all dated codes are stable. For example, the
  second withdrawal of the USA is only available as ``PARIS_2026_01`` and ``PARIS``
  so far, not as ``PARIS_2026``.
