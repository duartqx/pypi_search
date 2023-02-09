#!/usr/bin/env python3
"""
Script to be used on the command line, it uses the first 
argument to search for modules on pypi.org's websearch
"""

from pkg_resources import working_set
from re import findall
from urllib.request import urlopen

import sys


class ResultNotFoundError(Exception):
    pass


class PypiSearch:
    def __init__(self, q) -> None:
        self.q: str = q
        self.response: str = self.get_response()
        self.results: dict[str, list[str]] = self.get_results()
        self.range: int = min(len(self.results["vers"]), 5)

    def __repr__(self) -> str:

        if self.results["vers"]:
            # Get the installed list here so that I don't have to check for
            # self.results['vers'] inside the self._is_installed method.
            self.results["inst"] = self._is_installed()
            return (
                "".join(
                    "\n\033[1;32m%s\033[00m %s %s\n%s\n"
                    % (
                        self.results["names"][i],
                        self.results["vers"][i],
                        self.results["inst"][i],
                        self.results["desc"][i],
                    )
                    for i in range(self.range)
                )
                + "\n"
            )
            # The ANSI escape sequence ('\033[1;32m' and '\033[00m') makes the
            # module name in the results show up green instead of the default
            # white in the terminal
        else:
            # if self.results['vers'] is empty, that means no result was found.
            # self.results['vers'] is checked instead of self.results['names']
            # because the latter has a lot of junk from random links from
            # pypi.org site while self.results['vers'] only contains version
            # numbers found in the search
            raise ResultNotFoundError

    def get_response(self) -> str:
        """Returns the decoded data from a response got with
        urllib.request.urlopen to be scraped with a re.findall or re.finditer
        """
        url_base: str = "https://pypi.org/search/?q="

        try:
            response: str = urlopen(url_base + self.q).read().decode("UTF-8")
            return response
        except UnicodeEncodeError:
            raise ResultNotFoundError

    def get_results(self) -> dict[str, list[str]]:
        """Scrapes for name, version and description from the html received
        with get_response() using re.findall."""

        rsp: str = self.response

        names: list[str] = findall('__name">*(.*)</span>', rsp)
        versions: list[str] = findall('__version">*(.*)</span>', rsp)
        descriptions: list[str] = findall('__description">*(.*)</p>', rsp)

        return {"names": names, "vers": versions, "desc": descriptions}

    def _is_installed(self) -> list[str]:
        """Checks if modules on self.results are already installed or not"""

        inst_pkgs: list[str] = [pkg.key for pkg in working_set]
        inst: list[str] = [
            "[installed]" if self.results["names"][i].lower() in inst_pkgs else ""
            for i in range(self.range)
        ]
        return inst


def main() -> None:

    try:
        q: str = sys.argv[1]
        sys.stdout.write(PypiSearch(q).__repr__())
        sys.stdout.flush()
    except IndexError:
        sys.stderr.write(
            "\nEmpty search string.\n"
            + "Use pip search <module> or pypi_search <module>\n\n"
        )
        sys.stderr.flush()
        sys.exit(1)
    except ResultNotFoundError:
        sys.stderr.write("\nResult not found\n\n")
        sys.stderr.flush()
        sys.exit(1)


if __name__ == "__main__":

    main()
