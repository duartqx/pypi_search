#!/usr/bin/env python3
"""
Script to be used on the command line, it uses the first 
argument to search for modules on pypi.org's websearch
"""

from importlib import metadata
from re import findall
from typing import Literal, Optional, Self

import http.client
import sys


class ResultNotFoundError(Exception):
    pass


class HttpsRequest:
    def __init__(self, host: str) -> None:
        self.host: str = host
        self.method: Literal["GET", "POST"] = "GET"
        self.path: Optional[str] = None
        self.conn: Optional[http.client.HTTPSConnection] = None

    def get(self, path: str) -> Self:
        self.path = path
        self.method = "GET"
        return self

    def read(self) -> bytes:
        if self.conn is None:
            raise Exception("You should first start a context block")
        elif self.path is None:
            raise Exception("You should first set a path")

        self.conn.request(self.method, self.path)
        return self.conn.getresponse().read()

    def __enter__(self) -> Self:
        self.conn = http.client.HTTPSConnection(self.host)
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        if self.conn is not None:
            self.conn.close()


class PypiSearch:
    def __init__(self, q: str, max_results: int = 5) -> None:
        self.q: str = q
        self.response: str = self.get_response()
        self.results: dict[str, list[str]] = self.get_results()
        self.range: int = min(len(self.results["vers"]), max_results)

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
        try:
            with HttpsRequest("pypi.org").get(f"search/?q={self.q}") as req:
                return req.read().decode()
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

        inst_pkgs: list[str] = [p.name for p in metadata.distributions()]

        inst: list[str] = [
            "[installed]" if self.results["names"][i].lower() in inst_pkgs else ""
            for i in range(self.range)
        ]
        return inst


def main() -> None:
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="PypiSearch")
    parser.add_argument("query", help="The package name to search on Pypi.org")
    parser.add_argument(
        "-m",
        "--max_results",
        type=int,
        help="The max number of results to show",
        default=5,
    )

    args = parser.parse_args()

    try:
        print(PypiSearch(args.query, args.max_results), flush=True)
    except ResultNotFoundError:
        print("\nResult not found\n", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
