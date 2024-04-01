from operator import itemgetter
import gradio as gr
from dotenv import load_dotenv
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


# Load the .env file
load_dotenv()

# Initialize the llm and the database
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
db = SQLDatabase.from_uri("sqlite:////mnt/c/sqlite/db/shipping_company.db")

# Initialize the tools required for the chain. write_query will generate the SQL query, and execute_query will execute it.
write_query = create_sql_query_chain(llm, db)
execute_query = QuerySQLDataBaseTool(db=db)

# Create the chain
# Step 1: Generate the SQL query
generate_query = RunnablePassthrough.assign(query=write_query)

# Step 2: Execute the SQL query
execute_query_step = generate_query.assign(result=itemgetter("query") | execute_query)

# Step 3: Answer the user question
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, chat history, corresponding SQL query, and SQL result, answer the user question.
    Main communication langauge is Hebrew.

Question: {question}
History: {history}
SQL Query: {query}
SQL Result: {result}
Answer: """
)
chain = execute_query_step | answer_prompt | llm | StrOutputParser()



def invoke_chain(user_question, history):
    # Generate the SQL query
    print(generate_query.invoke({"question": user_question})["query"])

    # Get the response
    response = chain.invoke({"question": user_question, "history": history})

    # Return both the query and the response
    return response


demo = gr.ChatInterface(fn=invoke_chain, title="צ'אטבוט דאטה",
                        chatbot=gr.Chatbot(rtl=True),
                        textbox=gr.Textbox(label="שאלת משתמש", placeholder="הקלד שאלה", rtl=True))
demo.launch(share=True)
