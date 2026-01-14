

curl http://localhost:11434/api/show -d '{
  "name": "gpt-oss:20b"
}'> gpt.txt

curl http://localhost:11434/api/show -d '{
  "name": "mistral:latest"
}'> mistral.txt

curl http://localhost:11434/api/show -d '{
  "name": "qwen2.5-coder:latest"
}'> qwen.txt

curl http://localhost:11434/api/show -d '{
  "name": "llama3.2:latest"
}'> llama.txt