#!/usr/bin/env python

# todo: use generators
# todo: create tests

import logging
import os
import re
from collections import Counter
from collections import namedtuple
from typing import Optional

import doi


def main():
    rename_pdfs(safify())


errors = Counter()
Paper = namedtuple("Paper", ["path", "file", "doi", "url"], defaults=(None, None))


def get_pdfs_and_dois(path: str = ".") -> list:
    a = []
    for path, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pdf"):
                a.append(
                    Paper(path, file, doi.pdf_to_doi(os.path.join(path, file)), "")
                )
    return a


def clean_doi() -> list:
    b = []
    for paper in get_pdfs_and_dois():
        try:
            clean = doi.get_clean_doi(paper.doi)
        except TypeError:
            errors["type_error"] += 1
        else:
            b.append(
                Paper(paper.path, paper.file, clean, "")
            )  # todo: make code more functional
    return b


logger = logging.getLogger("doi")


def validate_doi(doi: str) -> Optional[str]:
    """We check that the DOI can be resolved by
    `official means <http://www.doi.org/factsheets/DOIProxy.html>`_. If so, we
    return the resolved URL, otherwise, we return ``None`` (which means the
    DOI is invalid).

    :param doi: Identifier.
    :returns: The URL assigned to the DOI or ``None``.
    """
    import json
    import urllib.parse
    import urllib.request
    from urllib.error import HTTPError

    url = f"https://doi.org/api/handles/{doi}"
    logger.debug("handle url %s", url)
    request = urllib.request.Request(url)

    try:
        result = json.loads(urllib.request.urlopen(request).read().decode())
    except HTTPError:
        raise ValueError("HTTP 404: DOI not found")
    else:
        urls = [v["data"]["value"] for v in result["values"] if v.get("type") == "URL"]
        return (doi, urls[0]) if urls else None


def validate() -> list:
    c = []
    for paper in clean_doi():
        try:
            doi, url = validate_doi(paper.doi)
        except:  # todo: handle InvalidURL better
            errors["invalid_url"] += 1
        else:
            c.append(Paper(paper.path, paper.file, doi, url))
    return c


def safe_filename(s):
    r"""/ \ :* " ? < >"""
    return re.sub(r"/", "_", s)


def safify() -> list:
    return [(x[0], x[1], safe_filename(x[2]) + ".pdf") for x in validate()]


def rename_pdfs(d: list) -> None:
    for paper in d:
        new = os.path.join(paper.path, paper.doi)
        if not os.path.exists(new):
            old = os.path.join(paper.path, paper.file)
            os.rename(old, new)


if __name__ == "__main__":
    main()
