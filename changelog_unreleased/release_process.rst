* Moved the release process into GitHub Actions. Maintainers now start a release from
  the Actions tab and pick ``patch``, ``minor`` or ``major`` instead of running
  ``tbump`` locally; publishing to PyPI uses trusted publishing and the citation
  information in the README is updated automatically once zenodo has minted the DOI.
* Regenerate all cached Python specs from the YAML files during the release, and check
  in CI that the two are in sync, so the shipped caches cannot go stale.
