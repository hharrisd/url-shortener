# Shortster Simplified

_A URL shortener service._

## Description

This service has three main functionalities:

1. To receive an original URL and return a shortened URL that points to the original one. The service could receive a
   valid slug or alias to customize the final URL.
2. To redirect from the generated URL to the target or original URL.
3. To provide statistics about the generated URLs.

The idea is to generate a data structure like a hashmap, that allows the relationship between the URL and a shortcode
and some constraints like uniqueness and availability of the shortcode.

The solution was built with **Django** and **Django REST Framework**. It uses an **SQLite** DB to persist the data.
The **secret** the
Python library was used to obtain random strings at a cryptographic level.

## Endpoints examples

### Creating a short URL

This functionality is used sending a **POST** request to `/submit/` endpoint with payload like

```json
{
  "url": "https://www.django-rest-framework.org/",
  "key": "DRF-HOME"
}
```

If the URL is valid and key (shortcode) is valid and available, the response will be:

```json
{
  "url": "https://www.django-rest-framework.org/",
  "key": "DRF-HOME",
  "shortened_url": "http://127.0.0.1:8000/DRF-HOME",
  "created_by": "user"
}
```

### Using the generated URL

The `/<shortcode>` endpoint will validate if the given shortcode exist and redirects the navigation to the original URL.
It also will register the last time the URL was visited and count how many times it was accessed.
Following the previous example, `http://127.0.0.1:8000/DRF-HOME` will redirect
to `https://www.django-rest-framework.org/`.

### Retrieving stats from a shortcode

The `/<shortcode>/stats` endpoint will retrieve when the URL was created when it was visited for the last time, and how
many
clicks or visits it has.

A GET request to `/DRF-HOME/stats` returns:

```json
{
  "key": "DRF-HOME",
  "target_url": "https://www.django-rest-framework.org/",
  "created_at": "2023-01-10 22:55:22",
  "last_visit": "2023-01-10 23:03:19",
  "clicks": 10
}
```

## Fulfill the User Stories

The [shortener/tests.py](shortener/tests.py) implements the unit tests that ensure compliance with the requirements.

## Some approaches to consider to have a service like this in a production environment

- Make the shortcode query case-insensitive would increase the number of shortcodes available.
- Some features could be added such as the expiration date of the links or activate or deactivate them.
- SQLite was used as the test database. For a more robust solution, PostgreSQL could be used, for example.
- Using a cache optimization solution like Redis would improve query performance from frequent redirects.
- Different DB instances could be deployed for reading and for writing to improve performance.
- As the logic of the service is not very complex, a serverless approach could be considered for this solution.