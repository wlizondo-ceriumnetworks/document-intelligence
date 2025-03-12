import azure.functions as func
import logging
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Azure AI Document Intelligence settings
ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

document_analysis_client = DocumentAnalysisClient(ENDPOINT, AzureKeyCredential(KEY))

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="analyze", methods=["POST"])
def analyze_document(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function for document analysis.")

    # Check for file in the request
    try:
        file = req.files.get("file")
        if not file:
            return func.HttpResponse("Please upload a file.", status_code=400)

        # Read file content
        file_content = file.read()

        # Analyze document using Azure AI Document Intelligence
        poller = document_analysis_client.begin_analyze_document(
            model_id="prebuilt-invoice",  # Use "prebuilt-read" for general text extraction
            document=file_content,
        )
        result = poller.result()

        # Extract and format the analysis results
        extracted_data = {}
        for idx, field in enumerate(result.fields.items()):
            extracted_data[field[0]] = {
                "value": field[1].value,
                "confidence": field[1].confidence,
            }

        return func.HttpResponse(
            body=str(extracted_data), status_code=200, mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error analyzing document: {str(e)}")
        return func.HttpResponse(
            f"Failed to analyze document: {str(e)}", status_code=500
        )
