# Author: S Sandeep Pillai (github.com/Corruption13)
import requests
from bs4 import BeautifulSoup
import time
import sys
from lxml.html import fromstring
# import threading
# from itertools import cycle             # Pulled out proxy switching till fixing an issue. Rest works fine.


'''
    This is a program that can scrape N number of books from Flipkart.com's "Best-seller books" list.
    You can pause the crawler at any time, it'll pick up from the last search page. Use this feature with caution,
    it's very buggy.
    ISSUES: Delete "backup.csv" in root folder if issues persist to refresh the data set.
    
    
    You may EDIT the two lines below to MODIFY the crawler for your needs.

'''

no_of_pages_to_scrape = 50  # Accepted values:  1 to 50
base_url = "https://www.flipkart.com/books/pr?sid=bks&marketplace=FLIPKARTpage%3D1"


'''
    HOW TO EDIT URL
    
    
    Edit the above "base_url" variable with that of other search category after modifying the url*
    EXAMPLE:
    To search educational books list, click on that in flipkart, and copy paste that url. 
    The URL during documentation was 
    "https://www.flipkart.com/books/educational-and-professional-books/pr?sid=bks,enp&otracker=categorytree"
    
    * MAKE SURE YOU ARE !NOT! ON PAGE 2 or ANOTHER PAGE, ensure you are on PAGE 1 when copying the URL!

'''


try:
    pageNO = open("LastPage.txt", 'r')
    print("Welcome back to my Flipkart scraper!")
    cur_page = int(pageNO.read())
    file = open("Data.csv", 'w+')
    backup = open('backup.csv', 'r')  # Creates a backup file.
    file.write(backup.read())
    backup.close()
except IOError:
    # File does not exist
    print("Welcome to My Flipkart scraper, new user!")
    cur_page = 1
    file = open("Data.csv", 'w+')
    file.write("URL, Price, Title, Author, Stars, Ratings Count, Reviews Count, Language, Binding, Publisher, Genre, ISBN10, ISBN13(Double Click to view), Pages, Edition\n")


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


print("Begin Scrape!")


def fcrawler(url):      # Main function that scrapes the url provided.

    try:
        source = requests.get(url)
        source_code = source.text                           # BS4 stuff, ignore.
        soup = BeautifulSoup(source_code, "lxml")

        for item in soup.find_all("title"):

            # print("URL = ", url)
            language = " "
            binding = " "
            publisher = " "
            genre = " "
            isbn13 = " "
            isbn10 = " "
            pages = " "
            edition = " "
            stars = " "
            rating = " "
            reviews = " "
            # Details of book

            price = soup.find("div", {"class": "_1vC4OE _3qQ9m1"}).string
            file.write(url + ',Rs: ' + price[1:].replace(',', ''))
            temp_title = soup.find("h1", {"class": "_9E25nV"}).find("span").contents
            imp_detail = str(temp_title[-1]).split(',')

            title = str(temp_title[0]).replace(',', '-')
            authors = str(imp_detail[2:])[2:-3].replace(',', ' and ')
            #file.write(', ' + item.string[:-37])
            file.write(', ' + title)
            file.write(', ' + authors)
            try:
                stars = soup.find("div", {"class": "_1i0wk8"}).string
                for i in soup.find_all("div", {"class": "row _2yc1Qo"}):
                    obj = i.string
                    if obj[-1] == "&":
                        rating = obj[:-10].replace(',', '')
                    else:
                        reviews = obj[:-8].replace(',', '')


            except Exception:
                pass
            print(title, "\nAuthors: ", authors, "\nPrice: ", price)
            print( stars, 'with', rating, 'votes and', reviews, 'reviews')
            for book in soup.find_all("li", {"class": "_2-riNZ"}):
                # print(book.string)  # Uncomment for messy console.
                detail = book.string.replace(",", " &")
                if detail[0:8] == "Language":
                    language = detail[10:]
                elif detail[0:7] == "Binding":
                    binding = detail[9:]
                elif detail[0:9] == "Publisher":
                    publisher = detail[11:]
                elif detail[0:5] == "Genre":
                    genre = detail[7:]
                elif detail[0:4] == "ISBN":
                    isbn_num = detail[6:].split('&')
                    isbn13 = str(isbn_num[0])  # Excel doesnt have 13 digit flat number, hence string
                    isbn10 = str(isbn_num[1])
                elif detail[0:5] == "Pages":
                    pages = detail[7:]
                elif detail[0:7] == "Edition":
                    edition = str(detail[9:]).replace(',', '-')
            file.write(',' + stars )
            file.write(',' + rating)
            file.write(',' + reviews)
            file.write(',' + language)
            file.write(',' + binding)
            file.write(',' + publisher)
            file.write(',' + genre)
            file.write(',' + isbn10)
            file.write(',' + isbn13)
            file.write(',' + pages)
            file.write(',' + edition)
            file.write('\n')
    except Exception:
        print("\nERROR, THE GIVEN URL - PAGE HAS ISSUE OR CUSTOM URL SET UP WRONG!\n")


def scrape_books(max_value):        # Number of books to be scraped
    global cur_page
    max_value = max_value + cur_page - 1
    page = cur_page
    print("Currently at", cur_page)
    counter = 40*(cur_page-1) + 1
    '''
    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    '''
    try:
        while page <= max_value and page <= 50:         # Flipkart only has 50 pages right now, change if future update.

            url = base_url + "&page=" + str(page)                  # URL Constructor
            '''
            proxy = next(proxy_pool)
            source = requests.get(url, proxies={"http": proxy})
            '''
            source = requests.get(url)
            source_code = source.text                   # BS4 stuff, ignore.
            soup = BeautifulSoup(source_code, "lxml")

            print("#Page-[", page, "] URL: ", url)
            for links in soup.find_all("a", {'class': "Zhf2z-"}):
                url = "https://www.flipkart.com" + links.get('href')
                print("\n[", counter, "]", end=" ")
                counter = counter + 1
                fcrawler(url)

            print('\n', "#"*10)

            page = page + 1

            cur_page = page
            data = open("Data.csv", 'r')
            back = open('backup.csv', 'w+')  # Creates a backup file incase you need to pause.
            back.write(data.read())
            temp = open("LastPage.txt", 'w+')
            temp.write(str(cur_page))
            temp.close(); back.close(); data.close()

            print("\nPage", page-1, "done!")

        print("\nSUCCESS!", no_of_pages_to_scrape, "pages crawled during this runtime!")
        print(cur_page-1, "number of pages scraped in total!")
        print("Thats a total of", counter-1, "books!")

    except KeyboardInterrupt:
            pageNO = open("LastPage.txt", 'w+')
            pageNO.write(str(cur_page))
            print("EXITING, SAVING CURRENT PROGRESS!")
            pageNO.close()
            sys.exit(0)


'''

END OF FUNCTION DEFINITIONS

'''


def main():

    start = time.time()

    scrape_books(no_of_pages_to_scrape)        # Number of books to be scraped
    end = time.time()
    pageNO = open("LastPage.txt", 'w+')
    pageNO.write(str(cur_page))
    print("\nEXITING, SAVING CURRENT PROGRESS!")
    pageNO.close()
    file.close()
    data = open("Data.csv", 'r')
    back = open('backup.csv', 'w+')  # Creates a backup file incase you need to pause.
    back.write(data.read())
    print("Thank you for using my crawler, send suggestions at github.com/Corruption13\n\n")
    print("TIME FOR EXECUTION == ", end - start)


main()
