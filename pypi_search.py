#!/usr/bin/env python3
'''
Script to be used on the command line, it uses the first 
argument to search for modules on pypi websearch
'''

from re import findall
from urllib.request import urlopen
from sys import argv, exit as sysexit

class Results:

    def __init__(self, q: str) -> None:
        self.q: str = q
        self.response: str = self.get_response()
        self.results: str = self.get_results()

    def __repr__(self) -> str:
        return self.results

    def get_response(self) -> str:
        ''' Returns the decoded data from a response got with
        urllib.request.urlopen to be scraped with a re.findall or re.finditer
        '''
        url_base: str = 'https://pypi.org/search/?q='

        response: str = ''

        try:
            response = urlopen(url_base + self.q).read().decode('UTF-8')
        except UnicodeEncodeError:
            pass
        return response

    def get_results(self) -> str:
        ''' Scrapes for name, version and description from the html received
        with get_response() using re.findall. '''
        if not self.response:
            return '\nResult not found\n'

        rsp: str = self.response

        names: list[str] = findall('__name">*(.*)</span>', rsp)
        versions: list[str] = findall('__version">*(.*)</span>', rsp)
        descriptions: list[str] = findall('__description">*(.*)</p>', rsp)

        # Since re.finditer returns a callable_iterator it's required to loop
        # through it or call next() to get the string. That was a problem when
        # the results were less than the range that I was using to loop
        # through, resulting in the exception handling to return 'Result not
        # found'

        if versions:
            return ''.join("\n\033[1;32m{}\033[00m {}\n{}\n".format(
                            names[i], versions[i], descriptions[i]) \
                            for i in range(min(len(versions),5)))
            # The ANSI escape sequence ('\033[1;32m' + nxt(na) + '\033[00m')
            # makes the module name in the results show up green instead of the
            # default white in the terminal
        else:
            # if ve is empty, that means no result was found. ve is checked
            # instead of na because na has a lot of junk from random links from
            # pypi.org site while ve only contains version numbers found in the
            # search
            return '\nResult not found\n'



if __name__ == '__main__':

    q = argv[1]
    if not q:
        # If a search string is not passed python q is an empty string, so a
        # little help is printed and the script exits with a return code of 1,
        # so that bash can know that an error ocurred
        print('\nEmpty search string.\n' + \
              'Use pip search <module> or pypi_search <module>\n')
        sysexit(1)
    print(Results(q))
