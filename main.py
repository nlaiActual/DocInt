import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult

load_dotenv()  # Load variables from .env

endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")
docUrl = os.getenv("DOC_URL")

document_analysis_client = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

poller = document_analysis_client.begin_analyze_document(
    "prebuilt-layout", AnalyzeDocumentRequest(url_source=docUrl)
)
result: AnalyzeResult = poller.result()