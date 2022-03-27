# Pypi Search

![pypi search](https://github.com/duartqx/images/blob/main/pypi-search.png?raw=true "pypi search")

Since the default 'pip search' inst working anymore and returns an error, I've made a simple python script called "pypi-search" that I use instead. It gets search results from pypi website and prints them to the terminal. \
Sourcing the bashfunction in my .bashrc allows me to keep using the command 'pip search module', because bash then calls my pypi-search script instead of pip(1), while it uses the original pip for anything other than a search.
