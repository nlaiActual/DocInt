import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

load_dotenv()

endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")
docUrl = os.getenv("DOC_URL")

document_analysis_client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

print("Doc URL:", docUrl)

# 👇 Use correct param name for SDK 1.0.2 — no "body=", must be "analyze_document_request="
poller = document_analysis_client.begin_analyze_document(
    model_id="prebuilt-invoice",
    body=AnalyzeDocumentRequest(
        url_source=docUrl
    )
)

result = poller.result()
print(result)
print("\n--- Extracted Invoice Fields ---\n")

if not result.documents:
    print("⚠️ No document-level results found.")
else:
    doc = result.documents[0]
    for field_name, field in doc.fields.items():
        # Try to get the most relevant value for each field type
        value = getattr(field, "value", None)
        if value is None:
            # Handle currency
            if "valueCurrency" in field and field["valueCurrency"]:
                value = f"{field['valueCurrency']['currencySymbol']}{field['valueCurrency']['amount']} ({field['valueCurrency']['currencyCode']})"
            # Handle address
            elif "valueAddress" in field and field["valueAddress"]:
                value = field["valueAddress"].get("streetAddress", str(field["valueAddress"]))
            # Handle string
            elif "valueString" in field:
                value = field["valueString"]
            # Handle date
            elif "valueDate" in field:
                value = field["valueDate"]
            # Handle phone number
            elif "valuePhoneNumber" in field:
                value = field["valuePhoneNumber"]
        confidence = getattr(field, "confidence", None)
        print(f"{field_name}: {value} (confidence: {confidence:.2f})" if value else f"{field_name}: None")

    invoice_total = doc.fields.get("InvoiceTotal")
    if invoice_total and "valueCurrency" in invoice_total and invoice_total["valueCurrency"]:
        currency = invoice_total["valueCurrency"]
        value = f"{currency['currencySymbol']}{currency['amount']} ({currency['currencyCode']})"
        confidence = invoice_total.get("confidence", 0)
        print(f"\nInvoice Total: {value} (confidence: {confidence:.2f})")
    else:
        print("\nInvoice Total not found.")
