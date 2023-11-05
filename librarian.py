import requests
import argparse
import os
import re
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
            return None, None, None
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
            authors = ', '.join(volume_info["authors"])
            link_val = volume_info.get('infoLink', '')

            return authors, isbn, link_val
    else:
        print(f"Failed to fetch data for title: {title}")
        return None, None, None

def main():
    parser = argparse.ArgumentParser(
                            prog='Library',
                            description='Build json books list')
    parser.add_argument('--output', default='completed_books.json', help='output filename')
    parser.add_argument('--list_name', default='Completed', help='list name')
    args = parser.parse_args()

    if "ACTION" not in os.environ:
        load_dotenv()

    # Trello API credentials
    API_KEY = os.environ["TRELLO_API_KEY"]
    API_SECRET = os.environ["TRELLO_OAUTH_SECRET"]
    TOKEN = os.environ["TRELLO_TOKEN"]

    # Trello board and list IDs
    BOARD_NAME = "Library"

    print(f"Librarian is parsing {BOARD_NAME} : {args.list_name}")

    try:
        with open(args.output, 'r') as f:
            json_books = json.load(f)
            existing_books = {
                frozenset({key: book[key] for key in book if key not in ["isbn", "link"]}.items())
                for book in json_books
            }
    except FileNotFoundError:
        existing_books = {}

    client = TrelloClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        token=TOKEN,
    )

    board = next(x for x in client.list_boards() if x.name == BOARD_NAME)
    completed_list = next(
        (lst for lst in board.list_lists() if lst.name == args.list_name), None
    )
    if not completed_list:
        print(f"List '{args.list_name}' not found in board")
        exit(1)

    completed_books = [
        {"name": card.name, "review": get_comments(card.comments)}
        for card in completed_list.list_cards()
    ]

    # Exit early if we have no new books
    completed_books_set = {frozenset(completed_book.items()) for completed_book in completed_books}
    if existing_books == completed_books_set:
        print(f"No Books or reviews added to the list, exiting without writing new {args.output}")
        return

    print(f"Retrieving metadata from google and writing to {args.output}")

    for book in completed_books:
        authors, isbn, link = get_book_info_from_title(book["name"])
        book["authors"] = authors
        book["isbn"] = isbn
        book["link"] = link

    ## Save to JSON file
    with open(args.output, 'w') as f:
       json.dump(completed_books, f, indent=2)
    
    print(f"Books have been successfully fetched and saved to {args.output}")


if __name__ == "__main__":
    main()
