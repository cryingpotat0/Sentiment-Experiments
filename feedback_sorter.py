import argparse
from google.cloud import language

# from oauth2client.client import GoogleCredentials
# credentials = GoogleCredentials.get_application_default()

def sentiment_text(text):
    """Detects sentiment in the text."""
    language_client = language.Client()

    # Instantiates a plain text document.
    document = language_client.document_from_text(text)

    # Detects sentiment in the document. You can also analyze HTML with:
    #   document.doc_type == language.Document.HTML
    sentiment = document.analyze_sentiment()

    print('Score: {}'.format(sentiment.score))
    print('Magnitude: {}'.format(sentiment.magnitude))


sentiment_text("barack obama is pissed off")