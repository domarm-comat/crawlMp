from crawlMp.crawlers.fileCrawler import FileSearchCrawler
from crawlMp.crawlMp import CrawlMp
from crawlMp.snippets.output import print_summary

def on_done(results):
  print_summary(results)

manager = CrawlMp(FileSearchCrawler, links=["/home"], num_proc=8, pattern="\\.zip$")
manager.start(on_done)