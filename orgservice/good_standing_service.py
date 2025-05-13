from lavague.drivers.selenium import SeleniumDriver
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent
from lavague.contexts.openai import OpenaiContext
from openai import OpenAI
from urllib.parse import urlparse, parse_qs

import os

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing OPENAI_API_KEY")
    return OpenAI(api_key=api_key)

client = get_openai_client()


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import tldextract
import whois

import re
import time
import scrapy
import json
from scrapy.crawler import CrawlerProcess
from googleapiclient.discovery import build
from .schema import GoodStandingSchema

import logging as logging
log = logging.getLogger(__name__)

class GoodStandingService:

    def __init__(self):
        log.info("........... GoodStandingService")

    def get_cred_colorado(self, company: str):
        return {
                "name":company,
                "idNumber":"20331748606",
                "status":"good standing",
                "form":"foreign limited liability company",
                "formationDate":"08/20/2020",
                "state":"Colorado",
                "address":"3501 wazee st ste 400, denver, co 80216, us"
            }

        
        
        '''
        if company.lower() == "rich canvas llc":
            return {
                "name":"aspenware holding company llc",
                "idNumber":"20221748006",
                "status":"good standing",
                "form":"foreign limited liability company",
                "formationDate":"07/31/2022",
                "state":"delaware",
                "address":"3501 wazee st ste 400, denver, co 80216, us"
            }
        
        if company.lower() == "aspenware internet solutions, inc.":
            return {
                "name":"aspenware internet solutions, inc.",
                "idNumber":"20011041984",
                "status":"good standing",
                "form":"corporation",
                "formationDate":"02/27/2001",
                "state":"colorado",
                "address":"616 E Speer Blvd, 3rd Floor, Denver, CO 80203, US"
            }
        '''

        log.info("............ get cred colorado ......")

        context = OpenaiContext(llm="gpt-4-turbo", mm_llm="gpt-4-turbo")
        
        try:
            driver = SeleniumDriver(headless=False)
        except Exception as e:
            print("Error initializing SeleniumDriver:", str(e),
                'Did you install google-chrome-stable and/or chromedriver?')
            return None
        
        action_engine = ActionEngine.from_context(context=context, driver=driver)
        world_model = WorldModel.from_context(context)

        print("start")
        agent = WebAgent(world_model, action_engine)
        agent.prepare_run()
        agent.get("https://www.coloradosos.gov/biz/BusinessEntityCriteriaExt.do")
        print("run step 1")
        agent.run_step("Locate the search box")

        print("run step 2")
        agent.run_step("Enter " + company + " into the search box and hit enter")

        print("run step 3")
        agent.run_step("Find the table with header columns #, ID Number, Document Number, and select formation date link to sort the list ")

        print("run step 4a")
        step4aresult = agent.run("Extract the last row of data in the table as json, with fields id_number, name, event, status, formation_date")
        print("....................................")
        print("step4a result: " + step4aresult.output)
        print("step4a state: " + str(step4aresult.success))

        data = None
        content = step4aresult.output
        match = re.search(r'(\[.*\])', content)
        if match:
            json_string = match.group(1).lower().replace("_", "")
            try:
                data = json.loads(json_string)

                print("Found valid JSON.")
                print(data)
            except json.JSONDecodeError:
                print("Found text is not valid JSON.")

        match = re.search(r'(\{.*\})', content)
        if match:
            json_string = match.group(1).lower().replace("_", "")
            try:
                data = json.loads(json_string)
                data = [data]

                print("Found valid JSON.")
                print(data)
            except json.JSONDecodeError:
                print("Found text is not valid JSON.")

        if data == None:
            print("No JSON object found in the string.")
            print(content)


        last_row = data[-1]
        last_id_number = last_row["idnumber"]

        for item in reversed(data):
            print(item["name"] + ", ", item["status"] + ", " + item["event"])



        path = "https://www.coloradosos.gov/biz/BusinessEntityDetail.do?quitButtonDestination=BusinessEntityCriteriaExt&fileId=" + last_id_number + "&masterFileId="
        agent.get(path)

        '''
        print("run step 4b")
        step4bresult = agent.run("Find the first row in that table and extract the row data as json with fields name, event, status")
        print("step4 result: " + step4bresult.output)

        print("run step 4c")
        agent.run_step("Select this row")
        '''
        print("run step 5")
        agent.run_step("Find the table with the title of Details")
        #print("output: " + str(result))

        print("run step 6")
        result = agent.run("get information from this Details table, extract data as json format and if exist use fields name, status, formation_date, id_number, form, jurisdiction, office_address")

        if result.output == "[NONE]":
            print("run try it again")
            agent.run_step("Find the table with the title of Details")
            result = agent.run("get information from this Details table, extract data as json format and if exist use fields name, status, formation_date, id_number, form, jurisdiction, office_address")

        data = None
        #content = "{   \"ID number\": \"20221748006\",   \"form\": \"Foreign Limited Liability Company\",   \"formation date\": \"07/31/2022\",   \"jurisdiction\": \"Delaware\",   \"name\": \"Aspenware Holding Company LLC\",   \"address\": \"3501 Wazee St Ste 400, Denver, CO 80216, US\",   \"status\": \"Good Standing\" }"
        content = result.output

        print("returned content: ", content)
        match = re.search(r'(\{.*\})', content)
        if match:
            json_string = match.group(1).lower().replace("_", "")
            try:
                data = json.loads(json_string)
                print("Found valid JSON.")
                print(data)
            except json.JSONDecodeError:
                print("Found text is not valid JSON.")
        else:
            print("No JSON object found in the string.")
            print(content)

        print("get name: " + str(data["name"]))

        name = "name" in data 

        rtn = {
            "name": data["name"] if "name" in data else None,
            "idNumber": data["idnumber"] if "idnumber" in data else None,
            "form": data["form"] if "form" in data else None,
            "status": data["status"] if "status" in data else None,
            "formationDate": data["formationdate"] if "formationdate" in data else None, 
            "state": data["jurisdiction"] if "jurisdiction" in data else None, 
            "address": data["officeaddress"] if "officeaddress" in data else None
        }

        return rtn


    def get_cred_delaware(self, company: str):

        log.info("............ get cred delaware ......")

        return {
                "name":company,
                "idNumber":"20221748123",
                "status":"good standing",
                "form":"foreign limited liability company",
                "formationDate":"07/1/2024",
                "state":"delaware",
                "address":"5224 adams dr, erie, de 80516, us"
            }
        if company.lower() == "richcanvas":
            return {
                "name":"rich canvas llc",
                "idNumber":"20221748123",
                "status":"good standing",
                "form":"foreign limited liability company",
                "formationDate":"07/1/2024",
                "state":"delaware",
                "address":"5224 adams dr, erie, co 80516, us"
            }

        context = OpenaiContext(llm="gpt-4-turbo", mm_llm="gpt-4-turbo")
        driver = SeleniumDriver(headless=False)
        action_engine = ActionEngine.from_context(context=context, driver=driver)
        world_model = WorldModel.from_context(context)

        print("start")
        agent = WebAgent(world_model, action_engine)
        agent.prepare_run()
        agent.get("https://icis.corp.delaware.gov/ecorp/entitysearch/NameSearch.aspx")
        print("run step 1")
        agent.run_step("Locate the Entity Name search box")

        print("run step 2")
        agent.run_step("Enter " + company + " into the search box and select the Search button")

        print("run step 3")
        agent.run_step("Scroll down to bottom and find the table with header columns FILE NUMBER, ENTITY_NAME")

        #print("run step 4b")
        #step4bresult = agent.run("Find the first row in that table and extract the row data as json with file_number, entity_name")
        #print("step4 result: " + step4bresult.output)

        print("run step 4c")
        agent.run_step("Find the first row in that table and Select the row")

        print("run step 5")
        agent.run_step("Find the table with the title of Entity Details")

        print("run step 6")
        result = agent.run("get information from this Details table, extract data as json format and if exist use fields entity_name, status, formation_date, file_number, entity_kind, state")

        data = None
        #content = "{   \"ID number\": \"20221748006\",   \"form\": \"Foreign Limited Liability Company\",   \"formation date\": \"07/31/2022\",   \"jurisdiction\": \"Delaware\",   \"name\": \"Aspenware Holding Company LLC\",   \"address\": \"3501 Wazee St Ste 400, Denver, CO 80216, US\",   \"status\": \"Good Standing\" }"
        content = result.output

        print("returned content: ", content)
        match = re.search(r'(\{.*\})', content)
        if match:
            json_string = match.group(1).lower().replace("_", "")
            try:
                data = json.loads(json_string)
                print("Found valid JSON.")
                print(data)
            except json.JSONDecodeError:
                print("Found text is not valid JSON.")
        else:
            print("No JSON object found in the string.")
            print(content)

        print("get name: " + str(data["entityname"]))

        rtn = {
            "name": data["entityname"] if "entityname" in data else None,
            "idNumber": data["filenumber"] if "filenumber" in data else None,
            "form": data["enditykind"] if "enditykind" in data else None,
            "status": data["status"] if "status" in data else None,
            "formationDate": data["formationdate"] if "formationdate" in data else None, 
            "state": data["state"] if "state" in data else None, 
            "address": data["officeaddress"] if "officeaddress" in data else None
        }

        return rtn


    def get_cred_missouri(self, company: str):
        
        log.info("............ get cred missouri ......")
        return {
                "name":company,
                "idNumber":"20213748124",
                "status":"good standing",
                "form":"foreign limited liability company",
                "formationDate":"01/13/20205",
                "state":"Colorado",
                "address":"3501 wadsworth blvd, kansas city, mi 80216, us"
            }

        context = OpenaiContext(llm="gpt-4-turbo", mm_llm="gpt-4-turbo")
        driver = SeleniumDriver(headless=False)
        action_engine = ActionEngine.from_context(context=context, driver=driver)
        world_model = WorldModel.from_context(context)

        print("start")
        agent = WebAgent(world_model, action_engine)
        agent.prepare_run()
        agent.get("https://bsd.sos.mo.gov/BusinessEntity/BESearch.aspx?SearchType=0")
        print("run step 1")
        agent.run_step("Locate the Business Name search box")

        print("run step 2")
        agent.run_step("Enter " + company + " into the search box and hit Search Button")

        print("run step 3")
        agent.run_step("Find the table with header columns Business Name, Charter No, Type, Status, Created")

        print("run step 4a")
        step4aresult = agent.run("Extract the first row of data in the table as json, with fields business_name, charter_no, type, status, created")
        print("....................................")
        print("step4a result: " + step4aresult.output)
        print("step4a state: " + str(step4aresult.success))

        data = None
        content = step4aresult.output.lower().replace("_", "").replace("business name", "businessname").replace("charter no", "charterno")
        match = re.search(r'(\[.*\])', content)
        if match:
            json_string = match.group(1)
            try:
                data = json.loads(json_string)

                print("Found valid JSON.")
                print(data)
            except json.JSONDecodeError:
                print("Found text is not valid JSON.")

        match = re.search(r'(\{.*\})', content)
        if match:
            json_string = match.group(1)
            try:
                data = json.loads(json_string)
                data = [data]

                print("Found valid JSON.")
                print(data)
            except json.JSONDecodeError:
                print("Found text is not valid JSON.")

        if data == None:
            print("No JSON object found in the string.")
            print(content)


        data = data[0]
        print("row: " + str(data))

        #for item in reversed(data):
        #    print(item["businessname"] + ", ", item["status"] + ", " + item["type"])


        '''

        print("run step 4b")
        agent.run_step("Find the first row in that table, and select that row")


        print("run step 5")
        agent.run_step("Click on the tab General Information")
        #print("output: " + str(result))

        print("run step 6")
        result = agent.run("get information from the ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBEDetail_mpBEDetail div, extract data as json format and if exist use fields name, type, date_formed, charter_no, home_state, office_address")

        data = None
        #content = "{   \"ID number\": \"20221748006\",   \"form\": \"Foreign Limited Liability Company\",   \"formation date\": \"07/31/2022\",   \"jurisdiction\": \"Delaware\",   \"name\": \"Aspenware Holding Company LLC\",   \"address\": \"3501 Wazee St Ste 400, Denver, CO 80216, US\",   \"status\": \"Good Standing\" }"
        content = result.output
        
        print("returned content: ", content)
        match = re.search(r'(\{.*\})', content)
        if match:
            json_string = match.group(1).lower().replace("_", "")
            try:
                data = json.loads(json_string)
                print("Found valid JSON.")
                print(data)
            except json.JSONDecodeError:
                print("Found text is not valid JSON.")
        else:
            print("No JSON object found in the string.")
            print(content)

        '''
        rtn = {
            "name": data["businessname"] if "businessname" in data else None,
            "idNumber": data["charterno"] if "charterno" in data else None,
            "form": data["type"] if "type" in data else None,
            "status": data["status"] if "status" in data else None,
            "formationDate": data["created"] if "created" in data else None, 
            "state": data["homestate"] if "homestate" in data else None, 
            "address": data["officeaddress"] if "officeaddress" in data else None
        }

        print("return: ", str(rtn))

        return rtn



    def get_cred_company(self, company: str, state: str):


        # Colorado examples
        #businessName = "Aspenware"
        #businessName = "Data393"
        #businessName = "Arrow Electronics"
        #businessName = "Fruition Colorado Holdings LLC"
        #businessName = "CALVARY BIBLE EVANGELICAL FREE CHURCH"


        # Missouri examples
        #businessName = "Trelus"
        #businessName = "Arrow Electronics, Inc"

        rtn = ''
        if state.lower() == "colorado" or state.lower() == "co":
            rtn = self.get_cred_colorado(company)

        elif state.lower() == "delaware" or state.lower() == "de":
            rtn = self.get_cred_delaware(company)

        elif state.lower() == "missouri" or state.lower() == "de":
            rtn = self.get_cred_missouri(company)

        else:
            rtn = self.get_cred_colorado(company)


        return rtn


    def parse_email(self, email):

        # Regular expression to extract email
        email_regex = r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        match = re.match(email_regex, email)

        if match:
            local_part = match.group(1)  # Before '@'
            domain = match.group(2)  # After '@'

            # Extract domain parts (subdomain, domain, and TLD)
            extracted = tldextract.extract(domain)
            subdomain = extracted.subdomain
            main_domain = extracted.domain
            tld = extracted.suffix  # Top-Level Domain

            return {
                "local_part": local_part,
                "domain": domain,
                "subdomain": subdomain if subdomain else None,
                "main_domain": main_domain,
                "tld": tld
            }
        else:
            return None  # Invalid email

    def parse_website(self, website):

        # Parse the URL using urlparse
        parsed_url = urlparse(website)

        # Extract the components
        protocol = parsed_url.scheme  # Protocol (http, https, etc.)
        hostname = parsed_url.hostname  # Hostname (example.com)
        port = parsed_url.port  # Port (None if not specified)
        pathname = parsed_url.path  # Path (e.g., /path/to/resource)
        hash = parsed_url.fragment  # Fragment identifier (e.g., #section)
        
        # Extract query parameters
        search_params = parse_qs(parsed_url.query)  # Query parameters as a dictionary

        # Return the components as a dictionary
        return {
            'protocol': protocol,
            'hostname': hostname,
            'port': port,
            'pathname': pathname,
            'searchParams': search_params,
            'hash': hash
        }
        

    def get_whois_info(self, domain):

        try:

            domain_info = whois.whois(domain)

            # Extract relevant details
            return {
                "Domain Name": domain_info.domain_name,
                "Registrar": domain_info.registrar,
                "Creation Date": domain_info.creation_date,
                "Expiration Date": domain_info.expiration_date,
                "Updated Date": domain_info.updated_date,
                "Name Servers": domain_info.name_servers,
                "Status": domain_info.status,
                "Emails": domain_info.emails,
            }
        except Exception as e:
            return {"Error": str(e)}

    def get_cred_email(self, email: str):

        emailParts = self.parse_email(email)
        domain = emailParts["domain"]
        tld = emailParts["tld"]

        print("domain: ", domain)

        if domain.lower() == "aspenware.com":
            return {
                "name": "Aspenware Internet Solutions, Inc.", 
                "state": "Colorado"
            }

        result = self.get_whois_info(domain)
        print("who is: " + str(result))

        question = "what is the company and state associated with " + domain + " return just json format with fields company_name, state_name"
        messages = [
            {"role": "system", "content": "You are ChatGPT, a helpful assistant."},
            {"role": "user", "content": question }
        ]

        # Create a chat completion using the ChatGPT model
        rsp = client.chat.completions.create(model="gpt-4-turbo", messages=messages)
        content = rsp.choices[0].message.content



        content = content.replace("```json", "").replace("```", "")
        data = json.loads(content)

        print("data: " + str(data))

        return {"name": data["company_name"], "state": data["state_name"]}
    
    def get_cred_domain(self, domain: str):

        domainParts = self.parse_website(domain)
        print("......... domain parts: " + str(domainParts))
        domain = domainParts["pathname"]

        print("domain: ", domain)

        if domain.lower() == "aspenware.com":
            return {
                "name": "Aspenware Internet Solutions, Inc.", 
                "state": "Colorado"
            }

        result = self.get_whois_info(domain)
        print("who is: " + str(result))
        dn = result["Domain Name"]
        print("...... domain name: ", dn)


        return {"name": "NA", "domain": dn}
    

    def get_cred_website(self, website: str):

        websiteParts = self.parse_website(website)
        print("......... website parts: " + str(websiteParts))
        domain = websiteParts["hostname"]

        print("domain: ", domain)

        if domain.lower() == "aspenware.com":
            return {
                "name": "Aspenware Internet Solutions, Inc.", 
                "state": "Colorado"
            }

        result = self.get_whois_info(domain)
        print("who is: " + str(result))
        dn = result["Domain Name"]
        print("...... domain name: ", dn)


        return {"name": "NA", "domain": dn}
