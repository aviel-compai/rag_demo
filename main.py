import requests
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

# Load the .env file
load_dotenv()

##########################################
# 1. Data loading
##########################################

# Download the "state of the union" text
url = "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/modules/state_of_the_union.txt"
res = requests.get(url)
with open("state_of_the_union.txt", "w") as f:
    f.write(res.text)

# Load the text
loader = TextLoader('./state_of_the_union.txt')
documents = loader.load()

#############################################
# 2. Split data to meaningful chunks
#############################################

# Split the text into chunks
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
chunks_text = [doc.page_content for doc in chunks]

#######################################
# 3. Create a vector store
#######################################
vectorstore = FAISS.from_texts(chunks_text, embedding=OpenAIEmbeddings())

#######################################
# 4. Create a retriever
#######################################
# Create a retriever object from the 'db' using the 'as_retriever' method.
# This retriever is likely used for retrieving data or documents from the database.
retriever = vectorstore.as_retriever()

#######################################
# 5. Create a pipeline
#######################################
template = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, say exactly 'Aviel asked me to say that I dont know'. 
Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""
prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

#####################################
# 6. Actual question answering
####################################

chain.invoke("What Biden think of Israel policy?")
