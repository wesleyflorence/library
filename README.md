# library
Reading books

## librarian.py

Librarian is a Python script that automates the process of fetching book titles and their reviews from a Trello board, querying for their ISBN and canonical links, and storing the information in a JSON file. It's designed to be run as a GitHub Action but can also be executed locally.

## Features

- Fetch book titles and reviews from a specified Trello board and list.
- Query the Google Books API to retrieve ISBNs and canonical volume links.
- Persist fetched book information to a `books.json` file.
- Automated execution via GitHub Actions on a schedule or manual dispatch.

## Requirements

- Python 3.x
- A Trello account and [API key](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/)
- A `.env` file or GitHub Secrets configured with Trello credentials

## Local Setup

1. Clone the repository to your local machine.
2. Install the dependencies by running `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory with your Trello API credentials:
   ```
   TRELLO_API_KEY=your_trello_api_key
   TRELLO_OAUTH_SECRET=your_trello_oauth_secret
   TRELLO_TOKEN=your_trello_token
   ```
4. Manage venv
```sh
# Activate venv
~/code/library main
❯ python3 -m venv venv

~/code/library main
❯ source venv/bin/activate

# Install deps
~/code/library main
❯ pip install -r requirements.txt

# Deactivate venv
~/code/library main
❯ deactivate
```
5. Run `python librarian.py` to execute the script.

## GitHub Action

The `.github/workflows/fetch-books.yml` file contains a GitHub Action setup to:

- Run the script daily at midnight UTC.
- Allow for manual execution via the GitHub Actions tab.

Make sure to set the Trello API credentials (`TRELLO_API_KEY`, `TRELLO_OAUTH_SECRET`, and `TRELLO_TOKEN`) in your repository's secrets to use the GitHub Action.

## Acknowledgements

- Trello, for their API and services.
- Google Books API, for providing book data.
