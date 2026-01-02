

curl http://localhost:11434/api/show -d '{
  "name": "chat:gpt-oss:20b"
}'> gpt.txt

curl http://localhost:11434/api/show -d '{
  "name": "mistral:latest"
}'> mistral.txt

curl http://localhost:11434/api/show -d '{
  "name": "llama3.2:latest"
}'> llama.txt