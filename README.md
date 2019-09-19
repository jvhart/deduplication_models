# deduplication_models

This file contains several sample record deduplication problems.  All data sets
were taken from the Python dedupio/dedupe package available at:

https://github.com/dedupeio/dedupe

That package was built to demonstrate appropriate use of the associated dedupe
package.  It involves using minimal dependencies and does not use several of
the packages commonly used for data analysis in Python (like pandas and numpy).
Those example are also focused primarily on deduplication implementation, rather
that specialized formulation of matching techniques.

The purpose of this repository is to perform dedupliction problems using typical
Pyton data analysis packages while looking more in depth into some of the
specialized deduplication techniques (for example, dataset specific targeted
cleaning, graph clustering, engulfing distances).  That said, the dedupe package
is a good one, and it would certainly be worth your time to understand how it
works as well.

A sample deduplication analysis is completed in the csv_example file, though
this deduplication is really only partially completed (see the
csv_example_deduplication.py for more information on its deficiencies).

To start working, make sure you have a Python IDE installed on your machine.  I
recommend Anaconda distribution to start.  You can go to the following link to
find installation instructions/documentation:

https://docs.anaconda.com/anaconda/install/

Spyder is the IDE included with this installation, which is sufficient to work
with these projects unless you prefer another.  Open a command prompt window, 
change directory to the folder containing this file and the requirements.txt 
file.  Execute the command

"pip install -r requirements.txt"

This will install the packages needed to work through the sample deduplciation
analysis.  After that, open Spyder (or whatever IDE you choose to work in), and
and open "csv_example_data_exploration.py" or "csv_example_data_deduplication.py"
files to start working.  Beyond that, Google is your friend in learning how to
use these packages.  There is a lot of good documentation and tips/tricks
available out there.

Each folder in the repository contains data for a deduplication problem.  The
challenge for each is to use any/all information in the data set (as well as
outside information if you see fit) to determine which records refer to the
same real life entity.

Complete your own deduplication analyses, and submit them using GitHub.  Put
your Python code and/or your analysis results in a folder with your name inside
the "Submissions" folder of the relevant deduplication problem.

A great way to  get started is to review the example provided in the csv_example
problem, and adapt that code to make solutions for a few of the other problems.
After that, try to make improvements on the deduplication.  Try to build
multiple deduplication passes, improve data cleaning, modify distance functions,
optimize thresholds and weights, etc.

If you complete all the examples in this file, there are others in the original
dedupio package mentioned above that include connecting to MySQL and PostgreSQL
databases.  This is a great way to further work on these kind of problems.
