Pypi_Search
Since the default 'pip search' does not work anymore and returns an error
I've made a simple python script called pypi-search that gets search
results from pypi website and prints to the terminal
Because of this bash function if I use the command pip search <module> 
bash then calls my pypi-search script instead of pip(1) and uses the
original pip for anything other than a search
