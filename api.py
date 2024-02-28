from fastapi import FastAPI
from pydantic import BaseModel
import logging
import time
import chainlit as cl 
import chromadb 
import requests 
import os
from chromadb.config import Settings
from datetime import datetime
from chromadb.utils import embedding_functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationQueue:
    def __init__(self, max_length=3):
        self.queue = []
        self.max_length = max_length

    def add_conversation(self, question, response=None):
        if response:
            conversation = f'[INST] {question} [/INST] "{response}"'
        else:
            conversation = f'[INST] {question} [/INST] '
        if len(self.queue) >= self.max_length:
            self.queue.pop(0)
        self.queue.append(conversation)

    def get_conversations(self):
        return ''.join(self.queue)

    def generate_prompt(self, doc, query):
        base_prompt = self.get_conversations()
        prompt = f"{base_prompt}[INST]Document:`{doc}`. Using the text in Document, answer the following question factually: {query}. Answer concisely at most in three sentences. Respond in a natural way, like you are having a conversation with a friend.[/INST]"
        return prompt

api_host = os.getenv("API_HOST")
api_port = os.getenv("API_PORT")
RAG_DB_PATH = os.getenv("DB_PATH")
EMB_PATH = os.getenv("EMB_PATH")

settings = chromadb.get_settings()
settings.allow_reset = True
db = chromadb.PersistentClient(path=RAG_DB_PATH, settings=settings)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMB_PATH, device="cpu")
collection = db.get_collection("HPE_press_releases", embedding_function=emb_fn)
titan_url = f"http://{api_host}:{api_port}/generate_stream"

cq = ConversationQueue()

def generate_response(query, 
                      n_results=1, 
                      max_doc_length=8500, 
                      no_repeat_ngram_size=0, 
                      sampling_topk=50, 
                      sampling_topp=0.95, 
                      sampling_temperature=0.3, 
                      repetition_penalty=1.0):
    """
    Generates a response for a given query by querying a document collection, sorting the results by date, and sending a formatted prompt to a text generation model with specified parameters.

    Parameters:
    - query (str): The query string for which the response is to be generated.
    - n_results (int): Number of results to query from the collection.
    - max_doc_length (int): Maximum length of the document to consider for generating the prompt.
    - no_repeat_ngram_size (int): Size of the no-repeat n-gram. Prevents the model from repeating the same n-grams.
    - sampling_topk (int): The top-k tokens to be considered for sampling by the model.
    - sampling_topp (float): The cumulative probability cutoff for token sampling by the model.
    - sampling_temperature (float): Sampling temperature to control randomness in token selection.
    - repetition_penalty (float): Penalty applied to repeated tokens to encourage diversity.

    Returns:
    - answer (str): The generated response based on the most relevant document found.
    """
    results = collection.query(query_texts=[query], n_results=n_results)
    
    date_strings = [i['Date'] for i in results['metadatas'][0]]
    date_objects = [datetime.fromisoformat(date_str) for date_str in date_strings]
    formatted_dates = [dt.strftime('%Y-%m-%d') for dt in date_objects]
    sorted_dates_with_indices = sorted(enumerate(zip(date_objects, formatted_dates)), key=lambda x: x[1][0], reverse=True)

    original_indices = [index for index, _ in sorted_dates_with_indices]
    results_x = [results["documents"][0][original_indices[0]]]
    results2 = "\n".join(results_x)[:max_doc_length]

    prompt = cq.generate_prompt(results2, query)
    logger.info("Generated prompt for text generation model.")
    
    params = {
        'generate_max_length': max_doc_length,
        'no_repeat_ngram_size': no_repeat_ngram_size,
        'sampling_topk': sampling_topk,
        'sampling_topp': sampling_topp,
        'sampling_temperature': sampling_temperature,
        'repetition_penalty': repetition_penalty
    }
    json = {"text": prompt, **params}
    response = requests.post(titan_url, json=json, stream=True)
    response.encoding = "utf-8"
    
    answer = response.content.decode('utf-8')
    logger.info("Received response from text generation model and added answer to conversation history.")
    return answer

app = FastAPI()

class Item(BaseModel):
    text: str

@app.post("/generate/")
async def generate(item: Item):
    api_start_time = time.time()
    logger.info(f"Received text: {item.text}")
    
    gen_start_time = time.time()
    answer = generate_response(item.text)
    gen_time_taken = time.time() - gen_start_time
    
    logger.info(f"Time taken to generate response: {gen_time_taken:.2f} seconds.")

    api_time_taken = time.time() - api_start_time
    logger.info(f"Total API call time: {api_time_taken:.2f} seconds.")
    return {"text": answer}