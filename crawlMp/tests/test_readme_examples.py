def test_example_blocking(fake_fs):
    from crawlMp.crawlers.fileCrawler import FileSearchCrawler
    from crawlMp.crawlMp import CrawlMp
    from crawlMp.snippets.output import print_summary

    manager = CrawlMp(FileSearchCrawler, links=["/home"], num_proc=8, pattern="\.zip$")
    manager.start()
    print_summary(manager.results)
    assert True


def test_example_non_blocking(fake_fs):
    from crawlMp.crawlers.fileCrawler import FileSearchCrawler
    from crawlMp.crawlMp import CrawlMp
    from crawlMp.snippets.output import print_summary

    def on_done(results):
        print_summary(results)

    manager = CrawlMp(FileSearchCrawler, links=["/home"], num_proc=8, pattern="\.zip$")
    manager.start(on_done)
    assert True
