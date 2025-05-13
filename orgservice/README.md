# MyOrgWallet Python Service

## Goals

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

### 2. Export OpenAI Key

```sh
export OPENAI_API_KEY='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'
```

### 3. Run Server

```sh
python3 manage.py runserver 8501
```
IN BROWSER:
'http://127.0.0.1:8501/creds/good-standing/company?company=desiredcompany&state=companylocation (colorado, delaware, or missouri)

or

'http://localhost:8501/creds/good-standing/company?company=desiredcompany&state=companylocation (colorado, delaware, or missouri)

Please change the desiredcompany and companylocation before hitting enter in the searchbar!!


