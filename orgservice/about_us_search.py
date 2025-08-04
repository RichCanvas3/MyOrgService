from googleapiclient.discovery import build
import os
from langchain_community.tools.playwright import NavigateTool
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain



my_cse_id = "1372926d87b644422"
dev_key = "AIzaSyCDwQUmWciwBx7X51EP1_FEppfXkrSpNhM"

def google_search(search_term, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=dev_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

AGENTQL_API_KEY = os.environ.get('AGENTQL_API_KEY')
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

from langchain_agentql.tools import ExtractWebDataBrowserTool
from playwright.async_api import async_playwright

async def create_async_playwright_browser_custom():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    return playwright, browser

async def asyncbrowser(prompt, url_tocheck, company):
    playwright, async_browser = await create_async_playwright_browser_custom()
    llm = ChatOpenAI(model="gpt-4-turbo-preview", api_key=OPENAI_API_KEY)
    try:
        extract_web_data_browser_tool = ExtractWebDataBrowserTool(async_browser=async_browser)
        navigate_tool = NavigateTool(async_browser=async_browser)
        await navigate_tool.ainvoke({"url": url_tocheck})
        extracted=await extract_web_data_browser_tool.ainvoke({"prompt": prompt})
       
        #print(f"Extracted data for {url_tocheck}:\n{extracted['about_section']}")
        
        document=[Document(page_content=extracted['about_section'], metadata={'title':f'{company}_about_us'})]
        prompt=ChatPromptTemplate.from_template("Summarize this About Us section: {context}")
        chain=create_stuff_documents_chain(llm, prompt)

        result=chain.invoke({'context':document})

    finally:
        await async_browser.close()
        await playwright.stop()

    return result
"""
async def main(company):
    print(f'Searching for {company}')
    results = google_search(company, my_cse_id, num=1, cr="countryUS", lr="lang_en")
    tasks=[]
    for result in results:
        print(result.get('link'))
        print(result.get('snippet'))
        url=result.get('link')
        tasks.append((asyncbrowser("the description or about section of the company or business", url, company)))
    gathered=await asyncio.gather(*tasks)
    await asyncio.sleep(0.1)

    return gathered, url
"""
async def main(company):
    print(f'Searching for {company}')
    results = google_search(company, my_cse_id, num=1, cr="countryUS", lr="lang_en")
    tasks=[]
    for result in results:
        print(result.get('link'))
        print(result.get('snippet'))
        url=result.get('link')
    
    return url

if __name__=='__main__':
    url=asyncio.run(main('Apple'))

    
    