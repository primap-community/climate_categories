* Raised the minimum ``pyparsing`` version to 3.2.3, the first release that does not use
  ``return`` inside a ``finally`` block. Python 3.14 flags that as a ``SyntaxWarning``
  (PEP 765), so older versions could not be imported cleanly on Python 3.14.
* Fixed a file descriptor leak: ``Categorization.conversion_to`` never closed the
  conversion CSV file it opened.
* Replaced deprecated ``pyparsing`` camelCase API calls with their current equivalents.
