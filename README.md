# Branch Feed

Pick your engineering branch (CSE, ECE, EEE, Mechanical, Civil) and get news,
hackathons and new technology for that branch in one place, instead of
searching three different sites.

Built for AZINHACK '26 with the **TinyFish Search API**.

## How it works

1. The student picks a branch.
2. The Flask backend sends branch-specific queries to the TinyFish Search API
   (news, hackathons, new tech).
3. Results are cleaned before they reach the page:
   - social media links (Instagram, Facebook, LinkedIn, etc.) are removed,
   - generic listing pages are dropped so individual hackathons show up,
   - official hackathon platforms (Unstop, Devfolio, Devpost, MLH) are ranked first.
4. The frontend (HTML/CSS/JS) shows the three sections.

The API key stays on the backend in a `.env` file and is never sent to the browser.

## Tech

- Backend: Python, Flask, requests, python-dotenv
- Frontend: HTML, CSS, vanilla JavaScript
- Data: TinyFish Search API

## Run locally

```
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`):

```
TINYFISH_API_KEY=your_key_here
```

Then:

```
python app.py
```

Open http://127.0.0.1:5000

## Project structure

```
app.py               Flask backend, calls TinyFish and filters results
templates/index.html page structure
static/style.css     styling
static/script.js     fetches /api/feed and renders the results
```

## Known limitations

- Search results are live, so some hackathons may already be past their
  registration date. Check the date on the official page.
- Adding a new branch only needs two entries in `app.py`
  (`BRANCH_TOPICS` and `BRANCH_HACK_THEMES`).

## Author

Keshav Gupta
