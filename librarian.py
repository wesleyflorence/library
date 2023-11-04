import requests
import os
import re
from requests import get
from trello import TrelloClient
from dotenv import load_dotenv
import json


def get_comments(comments):
    pattern = r"^review\s*[^a-zA-Z0-9]*"
    for comment in comments:
        text = comment["data"]["text"]
        if "Review" in text:
            return re.sub(pattern, "", text, flags=re.IGNORECASE)
    return None


def get_book_info_from_title(title):
    formatted_title = "+".join(title.split())
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{formatted_title}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Parse the response to find the ISBN and the canonical volume link
        items = data.get("items", [])
        if not items:
            print(f"No results found for title: {title}")
            return None, None
        else:
            # Assuming the first result is the desired book
            book = items[0]
            volume_info = book["volumeInfo"]
            industry_identifiers = volume_info.get("industryIdentifiers", [])
            isbn_13 = None
            isbn_10 = None
            # Loop through the industry identifiers to find ISBNs
            for identifier in industry_identifiers:
                if identifier["type"] == "ISBN_13":
                    isbn_13 = identifier["identifier"]
                elif identifier["type"] == "ISBN_10":
                    isbn_10 = identifier["identifier"]

            # Use the ISBN-13 if available, else fall back to ISBN-10
            isbn = isbn_13 if isbn_13 else isbn_10
            link_val = book.get("selfLink", "")

            return isbn, link_val
    else:
        print(f"Failed to fetch data for title: {title}")
        return None, None


def main():
    load_dotenv()

    # Trello API credentials
    API_KEY = os.environ["TRELLO_API_KEY"]
    API_SECRET = os.environ["TRELLO_OAUTH_SECRET"]
    TOKEN = os.environ["TRELLO_TOKEN"]

    # Trello board and list IDs
    BOARD_NAME = "Library"
    LIST_NAME = "Completed"

    client = TrelloClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        token=TOKEN,
    )

    board = next(x for x in client.list_boards() if x.name == BOARD_NAME)
    completed_list = next(
        (lst for lst in board.list_lists() if lst.name == LIST_NAME), None
    )
    if not completed_list:
        print(f"List '{LIST_NAME}' not found in board")
        exit(1)

    completed_books = [
        {"name": card.name, "review": get_comments(card.comments)}
        for card in completed_list.list_cards()
    ]

    for book in completed_books:
        isbn, link = get_book_info_from_title(book["name"])
        book["isbn"] = isbn
        book["link"] = link

    ## Save to JSON file
    with open('books.json', 'w') as f:
       json.dump(completed_books, f, indent=2)
    
    print('Books have been successfully fetched and saved to books.json')


if __name__ == "__main__":
    main()
