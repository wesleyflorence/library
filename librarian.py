import os
from trello import TrelloClient
from dotenv import load_dotenv
import json

load_dotenv()

# Trello API credentials
API_KEY = os.environ['TRELLO_API_KEY']
API_SECRET = os.environ['TRELLO_OAUTH_SECRET']
TOKEN = os.environ['TRELLO_TOKEN']

# Trello board and list IDs
BOARD_NAME = 'Library'
LIST_NAME = 'Completed'

client = TrelloClient(
    api_key=API_KEY,
    api_secret=API_SECRET,
    token=TOKEN,
)

board = next(x for x in client.list_boards() if x.name == BOARD_NAME)
completed_list = next((lst for lst in board.list_lists() if lst.name == LIST_NAME), None)
if not completed_list: 
    print(f"List '{LIST_NAME}' not found in board")
    exit(1)

completed_books = [{'name': card.name, 'desc': card.description} for card in completed_list.list_cards()]
print(completed_books)
#
## Save to JSON file
#with open('books.json', 'w') as f:
#    json.dump(books, f)
#
#print('Books have been successfully fetched and saved to books.json')
