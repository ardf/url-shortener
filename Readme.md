# URL Shortener Project

## Overview

This repository contains the backend implementation of a URL shortener project. The application provides the following features:

- **Register:** Users can create accounts by providing their email and password.
- **Login:** Registered users can log in using their credentials.
- **Create Short URLs:** Both authenticated users and guests can generate short URLs.
- **Redirect to Long URLs:** Short URLs created can be used to redirect to the original long URLs.
- **View Short URLs and Stats:** Authenticated users have access to a list of short URLs they've created along with associated statistics.

## Architecture

![High Level Architecture of the project](https://github.com/ardf/url-shortener/blob/master/url-shortner-service-architecture.drawio.png?raw=true)

## Usage

### Register

- Endpoint: `/register`
- Method: `POST`
- Parameters:
  - `email`: User's email
  - `password`: User's password

### Login

- Endpoint: `/login`
- Method: `POST`
- Parameters:
  - `email`: User's email
  - `password`: User's password

### Create Short URL

1. Authenticated Users

- Endpoint: `/create`
- Method: `POST`
- Parameters:
  - `long_url`: Original long URL
  - `custom_alias` (optional): Custom alias

2. Anonymous Users

- Endpoint: `/public-create`
- Method: `POST`
- Parameters:
  - `long_url`: Original long URL

### Redirect to Long URL

- Endpoint: `/l/<short_url>`
- Method: `GET`

### View Short URLs and Stats

- Endpoint: `/user/short-urls`
- Method: `GET`
- Authentication required

## Contributing

Feel free to contribute to the project by opening issues or submitting pull requests.

## License

This project is licensed under the MIT License.
