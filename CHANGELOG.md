<!--
SPDX-FileCopyrightText: 2019-2021 Pynguin Contributors

SPDX-License-Identifier: CC-BY-4.0
-->

# Pynguin Changelog

Please also check the [GitHub Releases Page](https://github.com/se2p/pynguin/releases)
for the source-code artifacts of each version.

## Pynguin 0.9.0

- Proper support for Python 3.9
- Improve branch-distance calculations for `byte` values
- Cleanup algorithm implementations

## Pynguin 0.8.1

- Regroup configuration options
- Improve branch-distance calculations for data containers
- Save *import coverage* to a separate output variable
- Delete some unused code
- Add warning notice to read-me file

## Pynguin 0.8.0

- *Breaking:* Renamed `RANDOM_SEARCH` to `RANDOM_TEST_SUITE_SEARCH` to select the 
  random-sampling algorithm based on test suites introduced in Pynguin 0.7.0.
 

- Improve input generation for collection types.
- Add an implementation of tournament selection for the use with DynaMOSA, MOSA, and 
  Whole Suite.
  
  For Whole Suite, on can choose the selection algorithm (either rank or tournament 
  selection) by setting the value of the `--selection` parameter.
- Add [DynaMOSA](https://doi.org/10.1109/TSE.2017.2663435) test-generation algorithm.
  
  It can be selected via `--algorithm DYNAMOSA`.
- Add [MIO](https://doi.org/10.1007/978-3-319-66299-2_1) test-generation algorithm.
  
  It can be selected via `--algorithm MIO`.
- Add a random sampling algorithm based on test cases.
  
  The algorithm is available by setting `--algorithm RANDOM_TEST_CASE_SEARCH`.  It 
  randomly picks one test case, adds all available fitness functions to it and adds 
  it to the MOSA archive.  If the test case is covering one fitness target it is 
  retrieved by the archive.  If it covers an already covered target but is shorter 
  than the currently covering test case for that target, it replaces the latter.
- Fix `OSError` from executors queue.
  
  The queue was kept open until the garbage collector delete the object.  This 
  caused an `OSError` because it reached the OS's limit of open resource handles.  
  We now close the queue in the test-case executor manually to mitigate this.
- Fix `__eq__` and `__hash__` of parameterised statements.
  
  Before this, functions such as `foo(a)` and `bar(a)` had been considered 
  equivalent from their equals and hash-code implementation, which only compared the 
  parameters and returns but not the actual function's name.
- Fix logging to work properly again.

## Pynguin 0.7.2

- Fixes to seeding strategies

## Pynguin 0.7.1

- Fix readme file

## Pynguin 0.7.0

- *Breaking:* Renamed algorithms in configuration options.
  Use `RANDOM` instead of `RANDOOPY` for feedback-directed random test generation 
  and `WHOLE_SUITE` instead of `WSPY` for whole-suite test generation.
- Add [MOSA](https://doi.org/10.1109/ICST.2015.7102604) test-generation algorithm.  
  It can be selected via `--algorithm MOSA`.
- Add simple random-search test-generation algorithm.
  It can be selected via `--algorithm RANDOM_SEARCH`.
- Pynguin now supports the usage of a configuration file (based on Python's 
  [argparse](https://docs.python.org/3/library/argparse.html)) module.
  Use `@<path/to/file>` in the command-line options of Pynguin to specify a 
  configuration file.
  See the `argparse` documentation for details on the file structure.
- Add further seeding strategies to extract dynamic values from execution and to use 
  existing test cases as a seeded initial population (thanks to 
  [@Luki42](https://github.com/luki42))

## Pynguin 0.6.3

- Resolve some weird merging issue

## Pynguin 0.6.2

- Refactor chromosome representation to make the subtypes more interchangeable
- Update logo art
- Fix for test fixture that caused changes with every new fixture file

## Pynguin 0.6.1

- Add attention note to documentation on executing arbitrary code
- Fix URL of logo in read me
- Fix build issues

## Pynguin 0.6.0

- Add support for simple assertion generation (thanks to [@Wooza](https://github.com/Wooza)).
  For now, assertions can only be generated for simple types (`int`, `float`, `str`,
  `bool`).  All other assertions can only check whether or not a result of a method
  call is `None`.
  The generated assertions are regression assertions, i.e., they record the return
  values of methods during execution and assume them to be correct.
- Provide a version-independent DOI on Zenodo in the read me
- Several bug fixes
- Provide this changelog

## Pynguin 0.5.3

- Extends the documentation with a more appropriate example
- Removes outdated code
- Make artifact available via Zenodo

## Pynguin 0.5.2

- Extends public documentation

## Pynguin 0.5.1

- Provides documentation on [readthedocs](https://pynguin.readthedocs.io/)

## Pynguin 0.5.0

- First public release of Pynguin

## Pynguin 0.1.0

Internal release that was used in the evaluation of our paper “Automated Unit Test
Generation for Python” for the
[12th Symposium on Search-Based Software Engineering](http://ssbse2020.di.uniba.it/)
