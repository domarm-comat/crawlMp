import re
from copy import copy

import pytest

from crawlMp.crawlers.crawler_fs import CrawlerFs
from crawlMp.snippets.output import print_summary, print_list


@pytest.mark.parametrize("links", [["/"]])
def test_print_summary(fake_fs, links, capsys):
    crawl = None
    for crawl in CrawlerFs(copy(links), max_depth=2):
        pass
    assert crawl is not None

    print_summary(crawl.results)
    captured = capsys.readouterr()
    expected = [550, 41, 2]
    expected_output = re.compile(
        f"Crawled in: (.*) s\nNumber of hits: {expected[0]}\nNumber of followed links: {expected[1]}\nNumber of skipped links: {expected[2]}\n")
    assert re.match(expected_output, captured.out) is not None


def test_print_summary_no_result(capsys):
    print_summary(None)
    captured = capsys.readouterr()

    expected_output = "No results...\n"
    assert expected_output == captured.out


@pytest.mark.parametrize("links", [["/"]])
def test_print_list(fake_fs, links, capsys):
    crawl = None
    for crawl in CrawlerFs(copy(links), max_depth=1):
        pass

    assert crawl is not None

    print_list(crawl.results)
    captured = capsys.readouterr()

    expected_output = """/pyproject.toml
/MANIFEST.in
/.gitmodules
/versioneer.py
/fs_dirs_numpy_repo.txt
/environment.yml
/LICENSE.txt
/CITATION.bib
/.gitignore
/files.txt
/setup.py
/azure-pipelines.yml
/.mailmap
/THANKS.txt
/pavement.py
/test_requirements.txt
/.ctags.d
/.travis.yml
/pytest.ini
/fs_numpy_repo.txt
/setup.cfg
/.gitattributes
/.hadolint.yaml
/INSTALL.rst.txt
/.lgtm.yml
/.gitpod.yml
/tox.ini
/site.cfg.example
/.clang-format
/linter_requirements.txt
/doc_requirements.txt
/README.md
/release_requirements.txt
/.coveragerc
/LICENSES_bundled.txt
/.codecov.yml
/azure-steps-windows.yml
/runtests.py
"""
    assert expected_output == captured.out
