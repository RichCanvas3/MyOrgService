import scrapy

class ColoradoSpider(scrapy.Spider):
    name = "colorado"

    # You pass the URL as a command-line argument with -a url=...
    def __init__(self, url=None, *args, **kwargs):
        super(ColoradoSpider, self).__init__(*args, **kwargs)
        if not url:
            raise ValueError("You must provide a URL with -a url=https://example.com")
        self.start_urls = [url]

    def parse(self, response):
          self.logger.info(f"Scraping: {response.url}")
     
          self.logger.info("\n== Tables ==")
          tables = response.css('table')
          if not tables:
               self.logger.info("No tables found on this page.")
               return
          for table_index, table in enumerate(tables, start=1):
               if table_index == 1: # Only scrape the first table (no idea why the colorado site has so many repeat tables)
                    rows = []
                    for row in table.css('tr'):
                         cells = row.css('th, td')
                         row_data = [cell.css('::text').get(default='').strip() for cell in cells]
                         row_data = [cell for cell in row_data if cell]  # Strip empty cells
                         if row_data:
                              if row_data not in rows:
                                   rows.append(row_data)

                    if rows:  # Only yield non-empty tables
                         print(f"\n--- Table {table_index} ---")
                         i=0 
                         cleaned_rows = [] 
                         for r in rows:
                              if i==0 or i==1 or i==9: #quick fix for repeat rows shwoing up, no idea why
                                   i+=1
                                   continue
                              else:
                                   i+=1
                                   cleaned_rows.append(r)
                                   print(" | ".join(r))
                         
               
                         #yield cleaned_rows  #yields all rows
                         #VVV yields only the rows we want
                         yield {'name': cleaned_rows[1][1],'idNumber':cleaned_rows[3][1], 'status': cleaned_rows[2][1], 'form': cleaned_rows[3][3], 'formationDate': cleaned_rows[2][3], 'state': cleaned_rows[4][3], 'address': cleaned_rows[5][1], 'website': response.url}

# Delaware's site is a bit different, so we might not be able to use a spider for it, doesnt have seperate pages for each company. 
# For now will just default to the base LLM method
class DelawareSpider(scrapy.Spider):
    name = "delaware"
     
    

    # You pass the URL as a command-line argument with -a url=...
    def __init__(self, url=None, *args, **kwargs):
        super(DelawareSpider, self).__init__(*args, **kwargs)
        if not url:
            raise ValueError("You must provide a URL with -a url=https://example.com")
        self.start_urls = [url]

    def parse(self, response):
          self.logger.info(f"Scraping: {response.url}")
     
          #extract all tables
          # Note: This is a simplified example. You may want to handle nested tables or other complexities.
          # For each table, we will extract the rows and their respective cells
          # and print them in a nicely formatted way.
          self.logger.info("\n== Tables ==")
          tables = response.css('table')
          if not tables:
               self.logger.info("No tables found on this page.")
               return
          for table_index, table in enumerate(tables, start=1):
               if table_index == 1: # Only scrape the first table (no idea why the colorado site has so many repeat tables)
                    rows = []
                    for row in table.css('tr'):
                         cells = row.css('th, td')
                         row_data = [cell.css('::text').get(default='').strip() for cell in cells]
                         row_data = [cell for cell in row_data if cell]  # Strip empty cells
                         if row_data:
                              if row_data not in rows:
                                   rows.append(row_data)

                    yield {
                         'type': 'table',
                         'table_number': table_index,
                         'rows': rows,
                         'website': response.url
                    }

class MissouriSpider(scrapy.Spider): #Missouri formatted in a really anoyying way (table within a weird selection menu, the html is god awful), so we have to do some extra work to get the data we want
     custom_settings = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
     'COOKIES_ENABLED': True,
     'HTTPERROR_ALLOWED_CODES': [403],
}

     name = "missouri"
    # You pass the URL as a command-line argument with -a url=...
     def __init__(self, url=None, *args, **kwargs):
        super(MissouriSpider, self).__init__(*args, **kwargs)
        if not url:
            raise ValueError("You must provide a URL with -a url=https://example.com")
        self.start_urls = [url]

     def parse(self, response):
          self.logger.info(f"Scraping: {response.url}")
          print(f"Scraping: {response.url}")
          containers = response.css('container')
          if not containers:
               self.logger.info("Nope.")
               return
          for i, container in enumerate(containers, 1):
               content = container.xpath('.//text()').getall()
               cleaned_content = ' '.join([text.strip() for text in content if text.strip()])

               rtn = {
                    'type': 'container',
                    'container_number': i,
                    'content': cleaned_content,
                    'website': response.url
               }
               print(type(rtn))
               yield rtn
          #extract all tables
          # Note: This is a simplified example. You may want to handle nested tables or other complexities.
          # For each table, we will extract the rows and their respective cells
          # and print them in a nicely formatted way.
          

                    
import multiprocessing
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher
from scrapy import signals

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def run_colorado_spider_process(companyNAME, return_dict):

     results = []
     def item_scraped(item):
          results.append(item)

     dispatcher.connect(item_scraped, signal=signals.item_scraped)
     
     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

     custom_settings = {
          'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
          'COOKIES_ENABLED': True,
          'HTTPERROR_ALLOWED_CODES': [403],
     }

     driver.get("https://www.coloradosos.gov/biz/BusinessEntityCriteriaExt.do")
     search = driver.find_element(by=By.ID,value="searchCriteria")
     search.send_keys(companyNAME)
     search.send_keys(Keys.RETURN)
     #button = driver.find_element(by=By.CLASS_NAME,value="button")
     #button.click()
     driver.save_screenshot("screenshot.png")  # Save a screenshot for debugging
     
     link = driver.find_element(by=By.CLASS_NAME,value='odd').find_element(by=By.CSS_SELECTOR,value='a').get_attribute('href')
     
     driver.get(link)
     driver.save_screenshot("screenshot2.png")  # Save a screenshot for debugging
     url=driver.current_url

     processco = CrawlerProcess(get_project_settings())
     processco.crawl(ColoradoSpider, url=url)
     processco.start()  # blocks until spider completes

     return_dict['results'] = results

def run_colorado_spider(companyNAME):
     manager = multiprocessing.Manager()
     return_dict = manager.dict()

     p = multiprocessing.Process(target=run_colorado_spider_process, args=(companyNAME, return_dict))
     p.start()
     p.join()

     return return_dict['results']

def run_missouri_spider(companyNAME):
     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

     custom_settings = {
          'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
          'COOKIES_ENABLED': True,
          'HTTPERROR_ALLOWED_CODES': [403],
     }

     driver.get("https://bsd.sos.mo.gov/BusinessEntity/BESearch.aspx?SearchType=0")
     search = driver.find_element(by=By.ID,value="ctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMainSingle_ppBESearch_bsPanel_tbBusinessName")
     search.send_keys(companyNAME)
     search.send_keys(Keys.ENTER)
     driver.save_screenshot("screenshot.png")  # Save a screenshot for debugging
     link = driver.find_element(by=By.XPATH,value="//a[@title='Select the link to view the Full Details for this Business']")
     link.click()
     driver.save_screenshot("screenshot2.png")  # Save a screenshot for debugging
     url=driver.current_url
    
     processmi = CrawlerProcess(get_project_settings())
     processmi.crawl(MissouriSpider, url=url)
     processmi.start()  # blocks until spider completes

def run_delaware_spider(companyNAME):

     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

     custom_settings = {
          'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
          'COOKIES_ENABLED': True,
          'HTTPERROR_ALLOWED_CODES': [403],
     }

     driver.get("https://icis.corp.delaware.gov/ecorp/entitysearch/NameSearch.aspx")
     search = driver.find_element(by=By.ID,value="ctl00_ContentPlaceHolder1_frmEntityName")
     search.send_keys(companyNAME)
     button = driver.find_element(by=By.ID,value="ctl00_ContentPlaceHolder1_btnSubmit")
     button.click()
     link = driver.find_element(by=By.ID,value="ctl00_ContentPlaceHolder1_rptSearchResults_ctl00_lnkbtnEntityName")
     link.click()
     url=driver.current_url

     processde = CrawlerProcess(get_project_settings())
     processde.crawl(DelawareSpider, url=url)
     processde.start()  # blocks until spider completes

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn') # Set the start method to 'spawn' for Windows compatibility
    # Example usage
    #run_missouri_spider("Trelus")
    result=run_colorado_spider("Mile High Runners")
    print(result)
    #run_delaware_spider('Aspenware')

