# playwright-test

Dockerfile & script for coding challenge.

----------------------------------------------------------------------

Steps to run:

Download and create a directory with all 3 files.

On command line inside the directory, Run "docker build -t ryanair-test ." and wait for image to build.

Run "docker run --rm -it ryanair-test" to run the tests

Docker container will be created and the output of the script will be printed to the terminal, including print statements of each step taken and some assertions for testing certain actions.

----------------------------------------------------------------------

The script "test_ryanair.py" can also be run in non-headless mode to visually see the actions taken by the script, (Note: need playwright installed locally for this).
Non-headless mode can be run with 2 steps:

Update line 28 of test_ryanair.py to the following:

browser = await playwright.firefox.launch(headless=False, slow_mo=1000)

Run the script in python with command "python test_ryanair.py"
