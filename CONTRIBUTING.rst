.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/primap-community/climate_categories/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

New categorizations
~~~~~~~~~~~~~~~~~~~

Especially welcome are new categorizations, which are not included in climate_categories
so far. Pull requests and issue reports at github are very welcome!

The categorizations are read from
`StrictYaml <https://github.com/crdoconnor/strictyaml>`_ files located at
``climate_categories/data/``.
You can write a yaml definition by hand, but ideally, categorizations are generated
from some canonical source automatically, so that the generation is reproducible and
transparent.
Scripts to generate categorizations are located in the ``data_generation`` folder and
write their results directly to ``climate_categories/data/``. For each data file, a
target should be included in the top-level Makefile. Do *not* include source pdfs with
non-free copyright licenses into the git repository. Instead, download them in the
data generation scripts (see ``data_generation/IPCC2006.py`` for an example how to
do that efficiently with caching).

Because all Categorizations are read in when importing ``climate_categories`` and
parsing StrictYaml files is not very efficient, the categories should be also stored
as cached Python files using the ``to_python`` instance method.
Run `make cache` to generate these from the YAML files.

New conversions
~~~~~~~~~~~~~~~

Especially welcome as well are new conversions between categorizations, which are not
included in climate_categories so far. Pull requests and issue reports at github are
very welcome!

The conversions are read from CSV files located at ``climate_categories/data/``.
You can write a CSV definition by hand, but ideally, conversions are also generated
from some canonical source automatically, so that the generation is reproducible and
transparent.
As the scripts to generate categorizations, the scripts to generate conversion files are
located in the ``data_generation`` folder and write their results directly to
``climate_categories/data/``.

Conversion files are read on demand and therefore no pickle files need to be generated.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Climate categories could always use more documentation, whether as part of the
official Climate Categories docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/primap-community/climate_categories/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that contributions are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `climate_categories` for local development.

1. Fork the `climate_categories` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/climate_categories.git

3. Install your local copy into a virtual environment. We use `uv`_ for dependency,
   environment and package management, so all you need installed is uv itself::

    $ cd climate_categories/
    $ make virtual-environment
    $ make install-pre-commit

   This creates ``.venv/`` from the committed ``uv.lock``. You never have to
   activate it: every ``make`` target runs its tools via ``uv run``, and you can do
   the same for one-off commands, e.g. ``uv run python``.

   Optional dependency groups are available for tasks that need them:
   ``--group docs`` for building the documentation and ``--group data-generation``
   for regenerating the categorizations.

.. _uv: https://docs.astral.sh/uv/

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass our tests and
   automatically format everything according to our rules::

     $ make lint

   Often, the linters can fix errors themselves, so if you get failures, run
   ``make lint`` again to see if any errors need human intervention.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Supported Python versions
-------------------------

We follow `NEP 29`_ for deciding which Python versions to support: everything
released in the last 42 months. The supported range is declared once, as
``requires-python`` in ``pyproject.toml``; the classifiers, the CI matrix in
``.github/workflows/ci.yml`` and the ``tox.ini`` envlist have to be kept in step
with it by hand.

The ``lowest-direct`` half of the CI matrix installs every dependency at the lower
bound declared in ``pyproject.toml``, so those bounds are tested. If you raise a
lower bound, say why in the commit message.

.. _NEP 29: https://numpy.org/neps/nep-0029-deprecation_policy.html

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring and check the generated
   API documentation.

Deploying
---------

A reminder for the maintainers on how to deploy. Everything happens in GitHub
Actions, so you need nothing installed locally and no credentials of your own.

1. Check that the `CI workflow`_ is green on ``main`` and that every change since the
   last release has a changelog fragment in ``changelog_unreleased/``.
2. Go to the `Release workflow`_, click *Run workflow*, leave the branch at ``main``
   and pick how the version should be increased:

   -  ``patch`` for bug fixes,
   -  ``minor`` for new categorisations,
   -  ``major`` for a major release and breaking changes.

That's it. The workflow then

-  regenerates all Python specs in ``climate_categories/data/`` from the YAML files,
   so the shipped caches cannot be out of date,
-  runs the test suite,
-  bumps the version in ``pyproject.toml`` and refreshes ``uv.lock``,
-  moves the fragments from ``changelog_unreleased/`` into ``CHANGELOG.rst``,
-  commits and tags the release on ``main``,
-  creates the GitHub release, which makes zenodo mint a new DOI,
-  publishes the package to PyPI, and
-  waits for zenodo and then updates the citation information in ``README.rst``.

.. _CI workflow: https://github.com/primap-community/climate_categories/actions/workflows/ci.yml
.. _Release workflow: https://github.com/primap-community/climate_categories/actions/workflows/release.yml

When something goes wrong
~~~~~~~~~~~~~~~~~~~~~~~~~

The release is only tagged after the caches have been regenerated and the tests have
passed, so a failure before that point leaves ``main`` untouched -- fix the problem
and run the workflow again.

Once the tag exists, the remaining jobs are independent and can be restarted on their
own with *Re-run failed jobs*:

-  **pypi** -- if a broken release did make it to PyPI, you can yank it: open the
   `release history`_, then options -> yank. Yanking hides the release from resolvers
   but leaves it installable for anyone who pins it exactly.
-  **citation** -- zenodo usually needs a few minutes to mint the DOI for the new
   release, and the job waits up to 15 minutes. If it times out anyway, run the
   `Update citation info workflow`_ by hand with the version number you released.

.. _release history: https://pypi.org/manage/project/climate-categories/releases/
.. _Update citation info workflow: https://github.com/primap-community/climate_categories/actions/workflows/update-citation.yml

Where the version number lives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``version`` in ``pyproject.toml`` is the only place the version is written down;
``climate_categories.__version__`` reads it back from the installed package metadata.
That means that in a development checkout ``__version__`` reflects the last
``uv sync``, not an unsynced edit to ``pyproject.toml``.
