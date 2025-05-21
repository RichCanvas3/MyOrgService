# MyOrgWallet Python Service

## Goals

* Use Agentic AI via OpenAI to obtain publically available company, email, domain, and website credentials in an efficient and autonomous manner
* Gather data to be used for ZK Proofs

## Requirements

* Python3
* pip
* Linux (preferrably Ubuntu)
* google-chrome-stable + chromedriver
* All of requirements.txt (into the venv)

## Setup

### 1. Create & Load Virtual Environment

```sh
sudo apt install python3-venv

python3 -m venv venv

source venv/bin/activate
```

### 2. Install Requirements and Dotenv

```sh
sudo venv/bin/pip install -r requirements.txt

```

### 3. Export OpenAI Key

```sh
export OPENAI_API_KEY='insert-your-open-api-key-here'
```

### 4. Run Server

```sh
python3 manage.py runserver 8501
```
## Running

### In Browser

  Go to http://127.0.0.1:8501 or http://localhost:8501

  These are both the base websites and will throw 404 errors until given input via the searchbar.

### Getting Company Cedentials

  Input http://127.0.0.1:8501/creds/good-standing/company?company=desiredcompany&state=companylocation

  into your searchbar, changing desiredcompany to whatever company you wish to look up, and companylocation to colorado, delaware, or missouri.

  If the server ever throws an error at any of these credential searches or just generally does not work, swith '127.0.0.1' out with 'localhost'.

  Remember to always change your queries from the 'desiredx' version before hitting enter in the searchbar!!!

### Getting Email Credentials

  Input http://127.0.0.1:8501/creds/good-standing/email?email=desiredemail

  into your searchbar, changing desiredemail to the email you want to search.

### Getting Domain Credentials

  Input http://127.0.0.1:8501/creds/good-standing/domain?domain=desireddomain

  into your searchbar, changing desireddomain to the domain you want to search.

### Getting Website Credentials

  Input http://127.0.0.1:8501/creds/good-standing/website?website=desiredwebsite

  into your searchbar, changing desiredwebsite to the website you want to search.
