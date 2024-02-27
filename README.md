
# Local RAG APP instructions

<<<<<<< HEAD
=======
`tar -xvf rag_db.tar.gz rag_db`
>>>>>>> 7117840 (update)
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
## (OPTIONAL) re-index the documents
### Run index_docs.sh

NOTE: this requires a GPU

`pip install langchain`
`bash index_docs.sh`



