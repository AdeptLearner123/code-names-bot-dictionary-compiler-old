#. Scrape oxford premium for a list of lemmas ``poetry run scrape-oxford-lemmas``

    #. The result of the scraper are already included
    #. You will need to set the cookie on the scraper

#. Create a filtered list of lemmas to download ``poetry run create-filtered-lemmas-list``
#. Download Oxford lemma entries ``poetry run download-lemmas-entries``

Downloading Wikipedia page titles and ids
#. Download dump from https://dumps.wikimedia.org/enwiki/latest/
#. Download MySQL and read the dump into a database
#. Run this SQL command: ``SELECT page_id, page_title FROM page WHERE page_namespace=0 AND page_is_redirect=0 INTO OUTFILE '/var/lib/mysql-files/wiki_pages.txt';``. This takes 21 min 2.03 sec to run.
#. Copy this file into ``/data/wiki_page_list_compiler/wiki_pages.txt``


Downloading wikipedia page views
#. Use an Ubuntu machine
#. ``poetry run download-wiki-page-views``