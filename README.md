# Overview #

Main aim of this project is to provide simple tool for multiprocess crawling.  
It can be used either as a tool for python project or as a command line tool.

# Concept #

This package was written to serve general purpose of crawling various resources.  
To achieve that, Crawler interface needs to be adopted.  
Just by implementing this interface, other Crawlers can be created and used with crawlMp manager.  
Resource Crawler is then used with CrawlWorker.   
Every crawler first enters entry point (link) and extract hits and links.  
If specified, pipeline of actions is executed on every hit. By default, hits are collected in SIMPLE_MODE only and
that's the fastest method to crawl as well.  
If other metadata related to hit is required, use MODE_EXTENDED.  
Other workers can pick up and follow link(s) from shared list asynchronously.

# What is in the package #

- Crawler interface
- Action interface
- File system Crawler, Actions with search capabilities
- scripts, providing easy access from command line

# Installation #

### Pip ###

`python3 -m pip install crawlMp`

### Git ###

`git clone https://github.com/domarm-comat/crawlMp.git`  
`cd crawlMp`  
`python3 setup.py install`

# Usage examples #

### Scripts ###

* Show help:  
  `search_fs_mp --help`
* Search for .zip files  
  `search_fs_mp \\.zip$`
* Get all .zip files in different directories  
  `search_fs_mp \\.zip$ -l /home /usr/share`
* Show search summary  
  `search_fs_mp \\.zip$ -l /home /usr/share -os`

### Python code (blocking) ###

```python
from crawlMp.crawlMp import CrawlMp
from crawlMp.crawlers.crawler_fs import CrawlerSearchFs
from crawlMp.snippets.output import print_summary

manager = CrawlMp(CrawlerSearchFs, links=["/home"], num_proc=8, pattern="\.zip$")
manager.start()
print_summary(manager.results)
```

### Python code (callback) ###

```python
from crawlMp.crawlMp import CrawlMp
from crawlMp.crawlers.crawler_fs import CrawlerSearchFs
from crawlMp.snippets.output import print_summary


def on_done(manager):
  print_summary(manager.results)


manager = CrawlMp(CrawlerSearchFs, links=["/home"], num_proc=8, pattern="\.zip$")
manager.start(on_done)
```

### Python code (actions) ###

```python
from crawlMp.crawlMp import CrawlMp
from crawlMp.actions.action_fs import Copy, Remove
from crawlMp.crawlers.crawler_fs import CrawlerSearchFs
from crawlMp.snippets.output import print_summary


def on_done(manager):
  print_summary(manager.results)


# Copy all found zip files and then remove them
# It's just to demonstrate usage of actions
actions = (Copy(target_dir="/home/domarm/zip_files"), Remove())
manager = CrawlMp(CrawlerSearchFs, links=["/home"], num_proc=8, pattern="\.zip$", actions=actions)
manager.start(on_done)
```

# Code coverage #

Run pytests and code coverage by executing following commands

```shell
coverage run -m pytest --rootdir ./crawlMp/tests/
coverage report > coverage.txt
```