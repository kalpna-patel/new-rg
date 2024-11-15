import os
import json
import argparse
import requests
from azure.storage.blob import BlobServiceClient
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def download_payload_from_url(url: str, local_path: str):
    """Download payload from a remote URL."""
    print(f"Downloading payload from {url}")
    response = requests.get(url)
    response.raise_for_status()  # Ensure we got a valid response
    with open(local_path, 'wb') as file:
        file.write(response.content)

def upload_to_blob(storage_account_name, container_name, file_path, blob_name):
    """Upload the file to Azure Blob Storage."""
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"File uploaded to Azure Blob Storage as {blob_name}")

def get_secret_from_key_vault(vault_uri, secret_name):
    """Retrieve a secret from Azure Key Vault."""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_uri, credential=credential)
    secret = client.get_secret(secret_name)
    return secret.value

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Ingest data to Azure Blob Storage.")
    parser.add_argument("fileList", help="Comma-separated list of files to ingest", type=str)
    parser.add_argument("jsonPayload", help="Local file or remote URL for the JSON payload", type=str)
    parser.add_argument("nameIngest", help="Ingestion name (schema name)", type=str)
    parser.add_argument("keyVaultUri", help="URI for Azure Key Vault", type=str)
    parser.add_argument("nameSignatureSecret", help="Name of the signature secret in Key Vault", type=str)
    parser.add_argument("storage_account_name", help="Azure Storage Account name", type=str)
    parser.add_argument("container_name", help="Azure Blob Storage container name", type=str)
    
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Download remote payload if necessary
    if args.jsonPayload.startswith("http"):
        download_payload_from_url(args.jsonPayload, "payload.json")
        args.jsonPayload = "payload.json"

    # Retrieve the signature secret (if required)
    signature_secret = get_secret_from_key_vault(args.keyVaultUri, args.nameSignatureSecret)
    print(f"Retrieved signature secret from Key Vault: {signature_secret}")
    
    # Prepare the file to upload to Blob Storage
    blob_name = f"{args.nameIngest}.json"
    upload_to_blob(args.storage_account_name, args.container_name, args.jsonPayload, blob_name)

if __name__ == "__main__":
    main()