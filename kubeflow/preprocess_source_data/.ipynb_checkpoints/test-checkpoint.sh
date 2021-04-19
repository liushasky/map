pip install -r requirements.txt
python data.py -b ~/work -t supplementary_data -i 4326
az acr build --registry $ACR_NAME --image kubeflow/nga-demo-pipeline/preprocessing:latest .