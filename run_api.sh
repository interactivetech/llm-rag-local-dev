# docker container: mendeza/mistral-llm-rag-ui:0.0.7
export API_HOST=10.182.1.48;
export API_PORT=8080;
export DB_PATH=/home/rag_db;
export EMB_PATH=/home/vector_model/e5-base-v2;
uvicorn api:app --reload --host 0.0.0.0 --port 8888