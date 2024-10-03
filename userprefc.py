import argparse
import mysql.connector
import requests
import subprocess
import time
from operator import itemgetter

JUST_TESTING = False
OPTION_FILE = "/etc/mysql/conf.d/analytics-research-client.cnf"


def get_open_wikis_list() -> list:
    # open_wikis = https://noc.wikimedia.org/conf/dblists/open.dblist - https://noc.wikimedia.org/conf/dblists/private.dblist
    try:
        open_wikis = requests.get(
            "https://noc.wikimedia.org/conf/dblists/open.dblist"
        ).text.split("\n")
        private_wikis = requests.get(
            "https://noc.wikimedia.org/conf/dblists/private.dblist"
        ).text.split("\n")

        # Remove the first element which is a comment
        open_wikis.pop(0)
        private_wikis.pop(0)

        for wiki in private_wikis:
            # If this wiki is in the open list, remove it
            if wiki in open_wikis:
                open_wikis.remove(wiki)
        return open_wikis
    except:
        print("Error getting list of wikis")
        raise Exception("Error getting list of wikis")


def get_wikis_list(wiki_list: str) -> list:
    try:
        if wiki_list == "open":
            return get_open_wikis_list()
        else:
            list_of_wikis = requests.get(wiki_list).text.split("\n")

            # Remove the first element which is a comment
            list_of_wikis.pop(0)

            return list_of_wikis
    except:
        print(f"Error getting list of wikis ({wiki_list})")
        raise Exception(f"Error getting list of wikis ({wiki_list})")


def get_target(wiki: str) -> tuple:
    try:
        result = subprocess.run(
            ["/bin/bash", "analytics-mysql", wiki, "--print-target"],
            stdout=subprocess.PIPE,
        )
        output = result.stdout.decode("utf-8").split(":")
        host = output[0].strip()
        port = output[1].strip()
        return host, port
    except:
        print(f"Error getting target for {wiki}")
        raise Exception(f"Error getting target for {wiki}")


def get_count(host: str, port: str, wiki: str, pref: str) -> int:
    try:
        cnx = mysql.connector.connect(
            host=host,
            port=port,
            database=wiki,
            option_files=OPTION_FILE,
        )
        cursor = cnx.cursor()

        cursor.execute(
            f"select count(up_user) from user_properties where up_property = '{pref}' and up_value = 1;"
        )

        result = cursor.fetchone()
        cnx.close()
    except Exception as e:
        print(f"Error getting count: {e}")
        return 0
    return result[0]


def run(cli_args) -> None:
    pref = cli_args.pref
    verbose = cli_args.verbose
    no_log = cli_args.no_log

    print(f"Getting counts of enabled preference '{pref}'", end="")
    if cli_args.all:
        print(" across all wikis")
        print("(this may take a moment — please wait...)")
        if JUST_TESTING:
            open_wikis = [
                "enwiki",
                "simplewiki",
                "frwiki",
                "dewiki",
                "metawiki",
                "zhwiki",
                "bewikibooks",
                "labswiki",
                "labtestwiki",
            ]
        else:
            open_wikis = get_wikis_list(cli_args.wiki_list)
        wiki_count = {}

        for wiki in open_wikis:
            try:
                host, port = get_target(wiki)
                count = get_count(host, port, wiki, pref)
            except:
                continue
            if verbose:
                print(f"[Verbose] Queried {wiki} and got {count}")
            if count > 0:
                wiki_count[wiki] = count
            time.sleep(0.1)
        wiki_count = sorted(wiki_count.items(), key=itemgetter(1), reverse=True)
        if not no_log:
            with open(f"userprefc_all_wikis.txt", "a") as f:
                f.write(
                    f"Getting counts of enabled preference '{pref}' across all wikis\n"
                )
        if cli_args.top:
            wiki_count = wiki_count[: cli_args.top]
            print(f"Top {cli_args.top} wikis:")
        for wiki, count in wiki_count:
            print(f"{wiki}: {count}")
            # Append to a log file
            if not no_log:
                with open(f"userprefc_all_wikis.txt", "a") as f:
                    f.write(f"{wiki}: {count}\n")
    else:
        wiki = cli_args.wiki
        print(f" on {wiki}")
        host, port = get_target(wiki)
        count = get_count(host, port, wiki, pref)
        print(f"{wiki}: {count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Don't log when checking all wikis",
    )
    parser.add_argument(
        "-p",
        "--pref",
        action="store",
        help="User preference to check",
    )
    parser.add_argument(
        "-w",
        "--wiki",
        action="store",
        help="Wiki to check",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Check all wikis",
    )
    parser.add_argument(
        "--top",
        action="store",
        help="Only list the top x wikis by enabled preference",
        type=int,
    )
    parser.add_argument(
        "--option-file",
        action="store",
        default="/etc/mysql/conf.d/analytics-research-client.cnf",
        help=f"Path to the MySQL option file (default: {OPTION_FILE})",
    )
    parser.add_argument(
        "--wiki-list",
        action="store",
        default="open",
        help='Wiki list to use — this is a dblist URL, or "open" (default: open, minus private wikis)',
    )
    parser.add_argument(
        "--just-testing",
        action="store_true",
        help="Use a hardcoded list of wikis for testing",
    )
    parser.add_argument(
        "--list-wikis",
        action="store_true",
        help="Return a list of all the open (non-private) wikis",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()
    OPTION_FILE = args.option_file
    JUST_TESTING = args.just_testing
    if args.list_wikis:
        wikis = get_open_wikis_list()
        for wiki in wikis:
            print(wiki)
        exit(0)
    if not args.pref:
        print("You must specify a preference (-p/--pref, e.g. 'editrecovery')")
        exit(1)
    if not args.wiki and not args.all:
        print("You must specify a wiki or use --all")
        exit(1)
    if args.top and not args.all:
        print("You can only use --top with --all")
        exit(1)
    run(args)
