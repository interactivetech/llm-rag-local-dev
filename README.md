
# Local RAG APP instructions

`tar -xvf rag_db.tar.gz rag_db`
# install vectordb locally

Use conatiner mendeza/mistral-rag-env:0.0.11-pachctl

get absolute path of current directory
`$pwd`
then run 

`docker run -it -p 8888:8888 -v $PWD:/home mendeza/mistral-rag-env:0.0.11-pachctl /bin/bash`

## inside docker container: 
cd /home

jupyter lab --ip=0.0.0.0 --port=8080 --NotebookApp.token='' --NotebookApp.password='' --allow-root

# run `notebooks/install_vector_embed.ipynb` to locally download the vectordb in /home directory. 
This will in turn be downloaded to $pwd directory

Next, stop jupyter notebook. we will run python scripts to create the vector database and run the UI application.

# run app
`pip install openai chainlit langchain`
`bash run_app.sh`

# Run the FastAPI endpoint
* `docker run -it -p 8888:8888 -v $PWD:/home mendeza/mistral-rag-env:0.0.11-pachctl /bin/bash`
* `cd /home`
* `pip install chromadb uvicorn fastapi sentence_transformers==2.2.2 openai chainlit`
* `bash run_api.sh`

Test API with curl request:
```
curl -v -X 'POST' \
  'http://127.0.0.1:8888/generate/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \

```
## (OPTIONAL) re-index the documents
### Run index_docs.sh

NOTE: this requires a GPU

`pip install langchain`
`bash index_docs.sh`