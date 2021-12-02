# Overview #

Main aim of this project is to provide simple tool for single or multiprocess resource crawling.  
It can be used either as a tool for python project or as a command line tool.  
Project comes with unit tests. 

# Concept #

This package was written to serve general purpose of crawling various resources.  
To achieve that, Crawler interface needs to be adopted.  
Just by implementing this interface, other Crawlers can be created and used with crawlMp manager.  
To use Crawler for resource crawling, it must be used in CrawlWorker.  
Crawled resource must be parallelized.  
Every crawler first enters entry point (link) and filter for hits and other links.  
Results of crawling are then stored in shared list.
Other workers can pick up and follow link from shared list.
For some cases, using only one single process is more effective than spawning multiple processes.  
CrawlMp manager does such a task effectively as well.  

# What is in the package #

- Crawler interface
- File system Crawler with search capabilities
- scripts, providing easy access from command line 

# Future development #

- Implementing more Crawlers
- Providing GUI

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
  * `search_fs_mp --help`
* Search for .zip files
  * `search_fs_mp \.zip$`
* Get all .zip files in different directories
  * `search_fs_mp \.zip$ -l /home /usr/share`
* Show search summary
  * `search_fs_mp \.zip$ -l /home /usr/share -o Summary`

### Python code (blocking) ###

```
from crawlMp.sources.fileCrawler import FileSearchCrawler
from crawlMp.sources.crawlMp import CrawlMp
from crawlMp.snippets.output import print_summary

manager = CrawlMp(FileSearchCrawler, links=["/home"], num_proc=8, pattern="\.zip$")
manager.start()
print_summary(manager.results)
```

### Python code (callback) ###

```
from crawlMp.sources.fileCrawler import FileSearchCrawler
from crawlMp.sources.crawlMp import CrawlMp
from crawlMp.snippets.output import print_summary

def on_done(results):
  print_summary(results)

manager = CrawlMp(FileSearchCrawler, links=["/home"], num_proc=8, pattern="\.zip$")
manager.start(on_done)
```
