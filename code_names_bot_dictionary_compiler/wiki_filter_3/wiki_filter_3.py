from code_names_bot_dictionary_compiler.download.caches import WikiPageViewCache
from config import WIKI_FILTERED_2, WIKI_FILTERED_3

PAGE_VIEW_THRESHOLD = 1e6
EXCLUDE_PAGES = set(["Main_Page"])


def main():
    with open(WIKI_FILTERED_2) as file:
        lines = file.read().splitlines()

        for line in lines:
            if len(line.split("\t")) < 2:
                print("Short line", line)

        titles = [line.split("\t")[1] for line in lines]
        title_to_line = {title: line for title, line in zip(titles, lines)}

    cache = WikiPageViewCache()
    title_to_views = cache.get_key_to_value()

    titles = filter(lambda title: title_to_views[title] > PAGE_VIEW_THRESHOLD, titles)
    titles = filter(lambda title: title not in EXCLUDE_PAGES, titles)
    lines = [title_to_line[title] for title in titles]

    with open(WIKI_FILTERED_3, "w+") as file:
        file.write("\n".join(lines))


if __name__ == "__main__":
    main()
