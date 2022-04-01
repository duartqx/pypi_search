#!/usr/bin/env python3
'''
Script to be used on the command line, it uses the first 
argument to search for modules on pypi websearch
'''

from re import finditer
from urllib.request import urlopen
from typing import Callable, Iterator, Match
from sys import argv, exit as _exit

class Results:

    def __init__(self, q):
        self.q: str = q
        self.response: str = self.get_response()
        self.results: str = self.get_results()

    def __repr__(self):
        return self.results

    def get_response(self) -> str:
        ''' Returns the decoded data from a response got with
        urllib.request.urlopen to be scraped with a re.findall or re.finditer
        '''
        url_base: str = 'https://pypi.org/search/?q='
        response: str = urlopen(url_base + self.q).read().decode('UTF-8')
        return response

    def get_results(self) -> str:
        ''' Scrapes for name, version and description from the html received
        with get_response() using re.finditer. Also worked with findall, but
        since it caches all results and I want to show only the first 5
        finditer could have better performance because it grabs the next result
        lazily '''

        na: Iterator[Match[str]] = finditer('__name">*(.*)</span>', self.response)
        ve: Iterator[Match[str]] = finditer('__version">*(.*)</span>', self.response)
        de: Iterator[Match[str]] = finditer('__description">*(.*)</p>', self.response)

        # Since re.finditer returns a callable_iterator it's required to loop
        # through it or call next() to get the string. Calling just group()
        # returns the full string with html tags included, and .group(1) is
        # just the right part inside the tag
        nxtg: Callable[[Iterator], str] = lambda i: next(i).group(1)

        try:
            res: Iterator[str] = ("\n\033[1;32m{}\033[00m {}\n{}\n".format(
                               nxtg(na), nxtg(ve), nxtg(de)) for _ in range(5))
            # The ANSI escape sequence ('\033[1;32m' + nxt(na) + '\033[00m')
            # makes the module name in the results show up green instead of the
            # default white in the terminal
            return ''.join(res)
        except RuntimeError:
            # RuntimeError is raised if the generator expression res raises a
            # StopIteration, that means finditer have not found results
            return '\nResult not found\n'


if __name__ == '__main__':

    q = argv[1]
    if not q:
        # If a search string is not passed python q is an empty string, so a
        # little help is printed and the script exits with a return code of 1,
        # so that bash can know that an error ocurred
        print('\nEmpty search string.\n' + \
              'Use pip search <module> or pypi_search <module>\n')
        _exit(1)
    print(Results(q))
