* ISO3: Added the parties to the Paris Agreement as ``PARIS``, which always refers to
  the current parties. For every month in which parties joined or left
  the Paris Agreement, there is a category ``PARIS_YYYY_MM`` containing the parties
  after all changes in that month took effect, based on the dates on which the
  Agreement entered into force for a party or its withdrawal took effect. The comments
  give the exact period during which each category describes the parties. The last
  category of every year is also available as ``PARIS_YYYY``, so that for example
  ``ISO3["PARIS_2026"]`` gives the parties after the second withdrawal of the USA took
  effect on 2026-01-27. Codes for the current or future months or years are not stable
  yet, which is noted in their comments.
