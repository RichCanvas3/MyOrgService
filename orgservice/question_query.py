#to connect to databse: sudo su postgres, then /usr/local/pgsql/bin/psql -d COBusiness

def sql_db_queryagent(question: str):
    from langchain_community.utilities import SQLDatabase

    try:
        db = SQLDatabase.from_uri("postgresql://postgres:31132005@localhost/COBusiness")
        print(db.dialect)
        db.run("SELECT * FROM BusinessEntities Limit 5;")
    except Exception as e:
        print('Error initializing database:', e)
        print('Check your database connection, tables, etc.')

    from langchain_community.agent_toolkits import SQLDatabaseToolkit

    '''
    DB_CONFIG = {
        'dbname': 'COBusiness',
        'user': 'postgres',
        'password': '31132005',
        'host': 'localhost',
        'port': 5432
    }
        
    TABLE_NAME = 'BusinessEntities'

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connected to PostgreSQL")
    except Exception as e:
        print("Database connection failed:", e)
        exit(1)
    '''
        
    from typing_extensions import TypedDict

    class State(TypedDict):
        question: str
        query: str
        result: str
        answer: str

    import getpass
    import os
    
    '''
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
    '''
    
    from langchain.chat_models.base import init_chat_model

    llm = init_chat_model("gpt-4-turbo", model_provider="openai")

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    tools = toolkit.get_tools()
    
    import ast
    import re

    def query_as_list(db, query):
        res = db.run(query)
        res = [el for sub in ast.literal_eval(res) for el in sub if el]
        res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
        return list(set(res))

    #entitynames = query_as_list(db, "SELECT entityname FROM BusinessEntities")

    from langchain.agents.agent_toolkits import create_retriever_tool

    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    from langchain_core.vectorstores import InMemoryVectorStore

    #vector_store = InMemoryVectorStore(embeddings)
    '''
    _ = vector_store.add_texts(entitynames)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    description = (
        "Use to look up values to filter on. Input is an approximate spelling "
        "of the proper noun, output is valid proper nouns. Use the noun most "
        "similar to the search."
    )
    retriever_tool = create_retriever_tool(
        retriever,
        name="search_proper_nouns",
        description=description,
    )
    '''
    print("Using Agent-based prompts.")

    system_message = """
    You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct {dialect} query to run,
    then look at the results of the query and return the answer. Unless the user
    specifies a specific number of examples they wish to obtain, always limit your
    query to at most {top_k} results.

    You can order the results by a relevant column to return the most interesting
    examples in the database. Never query for all the columns from a specific table,
    only ask for the relevant columns given the question.

    You MUST double check your query before executing it. If you get an error while
    executing a query, rewrite the query and try again.

    When querying for names, use an ILIKE search first with '%' on both sides of the initial queried name.

    If the ILIKE search comes back with two or more results, pick the first result.

    When querying for entity type, if the original question was about 'LLCs' and no results came back, 
    change 'LLCs' to 'DLLCs' and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
    database.

    To start you should ALWAYS look at the tables in the database to see what you
    can query. Do NOT skip this step. Only ever query the table BusinessEntities

    Then you should query the schema of the table BusinessEntities.

    If you need to filter on a proper noun like a Name, you must ALWAYS first look up 
    the filter value using the 'search_proper_nouns' tool! Do not try to 
    guess at the proper name - use this function to find similar ones.
    """.format(
        dialect=db.dialect,
        top_k=100,
        table_info='BusinessEntities',
    )

    from langchain_core.messages import HumanMessage
    from langgraph.prebuilt import create_react_agent

    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt.tool_node import ToolNode

    #tools.append(retriever_tool)

    agent_executor = create_react_agent(llm, tools, prompt=system_message)

    query=question

    messagelist=[]
    for step in agent_executor.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()
        messagelist.append(step["messages"][-1])

    return messagelist[-2].content

if __name__=='__main__':
    question=input()
    result=sql_db_queryagent(question)
    info=result.strip('[').strip(']').strip('(').strip(')').split(', ')
    print(info)

#Give me the info for Aspenware Holding Company LLC. Include entityname, entityid, entitystatus, entitytype, entityformdate, principalstate, principaladdress, principalcity, and principalzipcode in that order
    