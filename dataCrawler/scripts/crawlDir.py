from dataCrawler.backend.dirCrawler import DirCrawler


for crawler in DirCrawler("/home/domarm", max_depth=2):
    ...
print(crawler.links_followed)