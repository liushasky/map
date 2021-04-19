### Create a volume to mount external storage to the kubeflow cluster
NAMESPACE=pitcrew-kubeflow
ADLS_ACCOUNT_NAME=pitcrewstorage
ADLS_ACCOUNT_KEY=hB8d+muYJy4yUey6P4fWLEhi/iexF20seH2AIWGbw0jNq89amrbyAfYegTuTWWlXKVVGEqWpFysQJfpuOHsJbA==
kubectl create secret generic azure-fileshare-secret --from-literal=azurestorageaccountname=$ADLS_ACCOUNT_NAME --from-literal=azurestorageaccountkey=$ADLS_ACCOUNT_KEY -n $NAMESPACE
kubectl apply -f pvc.yaml

### Build images utlized in the pipeline
ACR_NAME=pitcrewacr
az login
cd preprocess_source_data
az acr build --registry $ACR_NAME --image kubeflow/nga-demo-pipeline/preprocessing:latest .
cd ..

cd extract_target_data
az acr build --registry $ACR_NAME --image kubeflow/nga-demo-pipeline/extracting:latest .
cd ..

cd geo_merge
az acr build --registry $ACR_NAME --image kubeflow/nga-demo-pipeline/merging:latest .
cd ..

cd ingest
az acr build --registry $ACR_NAME --image kubeflow/nga-demo-pipeline/ingesting:latest .
cd ..

### Compile the pipeline
python pipeline.py
