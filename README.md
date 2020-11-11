# HacScraper
Home Access Center Scraper

# Hosting
This version is **only** for self hosting and you should not use this for accessing **anyone** but your own's grades

## Requirements
- Python 3.8 + (utilizes new asyncio features)
> Flask + Scrapy (full back end)
- npm (React)
> Dasboard (full front end)
- MongoDB Server
> Any approved Mongo release is compatible but course data uses $aggregate features only available in Mongo 4.x+

# Features 

    - notify users
    - Display grades faster & better
    - graph grades in classes over time 
    - grade weight

# TODO
    - Build Scraper 
        - Login
            - Auth
            - Ratelimiting 10/m MAX
        - Periodically fetch
