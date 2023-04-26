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

Report bugs at https://github.com/pik-primap/climate_categories/issues.

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
official Climate categories docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/pik-primap/climate_categories/issues.

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

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper
   installed, this is how you set up your fork for local development::

    $ cd climate_categories/
    $ make virtual-environment
    $ make install-pre-commit

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

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring and check the generated
   API documentation.
3. The pull request will be tested on python 3.9, 3.10, and 3.11.

Deploying
---------

.. highlight:: shell

A reminder for the maintainers on how to deploy.

1.  Commit all your changes.
2.  Run ``tbump X.Y.Z``.
3.  Wait a bit that the release on github and zenodo is created.
4.  Run ``make README.rst`` to update the citation information in the README from the
    zenodo API. Check if the version is actually correct, otherwise grab a tea and
    wait a little more for zenodo to mint the new version. Once it worked, commit the
    change.
5.  Upload the release to pyPI: ``make release``
