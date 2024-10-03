# userprefc.py
Assumes you're on a WMF [analytics cluster client node](https://wikitech.wikimedia.org/wiki/Data_Platform/Systems/Cluster) (e.g. [stat1011](https://wikitech.wikimedia.org/wiki/Stat1011))

## Help
```
$ python userprefc.py -h
userprefc.py v1.0
Made with ♥ by TheresNoTime

usage: userprefc.py [-h] [--no-log] [-p PREF] [-w WIKI] [-a] [--top TOP] [--option-file OPTION_FILE] [--wiki-list WIKI_LIST]
                    [--just-testing] [--list-wikis] [-v] [--info]

Get user preference counts per wiki (or across all wikis)

optional arguments:
  -h, --help            show this help message and exit
  --no-log              Don't log when checking all wikis
  -p PREF, --pref PREF  User preference to check
  -w WIKI, --wiki WIKI  Wiki to check
  -a, --all             Check all wikis
  --top TOP             Only list the top x wikis by enabled preference
  --option-file OPTION_FILE
                        Path to the MySQL option file (default: /etc/mysql/conf.d/analytics-research-client.cnf)
  --wiki-list WIKI_LIST
                        Wiki list to use — this is a dblist URL, or "open" (default: open, minus private wikis)
  --just-testing        Use a hardcoded list of wikis for testing
  --list-wikis          Return a list of all the open (non-private) wikis
  -v, --verbose         Enable verbose logging
  --info                Get info/where to report bugs/etc.
```

## Examples
```
$ python userprefc.py --pref editrecovery --wiki enwiki
userprefc.py v1.0
Made with ♥ by TheresNoTime

Getting counts of enabled preference 'editrecovery' on enwiki
enwiki: [snipped]
```

```
$ python userprefc.py --pref editrecovery --all --just-testing --verbose --no-log --top 3
userprefc.py v1.0
Made with ♥ by TheresNoTime

Getting counts of enabled preference 'editrecovery' across all wikis
(this may take a moment — please wait...)
[Verbose] Queried enwiki and got [snipped]
[Verbose] Queried simplewiki and got [snipped]
[Verbose] Queried frwiki and got [snipped]
[Verbose] Queried dewiki and got [snipped]
[Verbose] Queried metawiki and got [snipped]
[Verbose] Queried zhwiki and got [snipped]
[Verbose] Queried bewikibooks and got [snipped]
[Verbose] Queried labswiki and got [snipped]
Error getting target for labtestwiki
Top 3 wikis:
enwiki: [snipped]
metawiki: [snipped]
frwiki: [snipped]
```
