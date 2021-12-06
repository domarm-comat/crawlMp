# Overview #

Main aim of this project is to provide simple tool for multiprocess crawling.  
It can be used either as a tool for python project or as a command line tool.  

# Concept #

This package was written to serve general purpose of crawling various resources.  
To achieve that, Crawler interface needs to be adopted.  
Just by implementing this interface, other Crawlers can be created and used with crawlMp manager.  
Resource Crawler is then used with CrawlWorker.   
Every crawler first enters entry point (link) and filter for hits and other links.  
Results of crawling are then stored in shared list.  
By default, hits are collected in SIMPLE_MODE only and that's the fastest method to crawl as well.  
If other metadata related to hit is required, use MODE_EXTENDED.  
Other workers can pick up and follow link from shared list.  
For some cases, using only one single process is more effective than spawning multiple processes.  
CrawlMp does it effectively as well.  

# What is in the package #

- Crawler interface
- File system Crawler with search capabilities
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
from crawlMp.crawlers.fileCrawler import FileSearchCrawler
from crawlMp.crawlMp import CrawlMp
from crawlMp.snippets.output import print_summary

manager = CrawlMp(FileSearchCrawler, links=["/home"], num_proc=8, pattern="\\.zip$")
manager.start()
print_summary(manager.results)
```

### Python code (callback) ###

```python
from crawlMp.crawlers.fileCrawler import FileSearchCrawler
from crawlMp.crawlMp import CrawlMp
from crawlMp.snippets.output import print_summary

def on_done(results):
  print_summary(results)

manager = CrawlMp(FileSearchCrawler, links=["/home"], num_proc=8, pattern="\\.zip$")
manager.start(on_done)
```

# Code coverage #

Run pytests and code coverage by executing
```shell
coverage run -m pytest --rootdir ./crawlMp/tests/
coverage report > coverage.txt
```