from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


async def gdoc_content_by_id(doc_id, token):
    creds = Credentials(token=token)
    try:
        service = build("docs", "v1", credentials=creds)
        document = service.documents().get(documentId=doc_id).execute()
        content = document.get('body').get('content')
        return extract_text(content)
    except HttpError as err:
        raise err


async def list_all_gdocs(token, pageSize, pageToken):
    creds = Credentials(token=token)
    try:
        service = build("drive", "v3", credentials=creds)
        results = (
            service.files()
            .list(
                q="mimeType='application/vnd.google-apps.document'",
                pageSize=pageSize,
                pageToken=pageToken if pageToken else None,
                fields="nextPageToken,files(id,name)",
            )
            .execute()
        )
        return results.get("files", []), results.get("nextPageToken")
    except HttpError as err:
        raise err


def extract_text(elements):
    text = ''
    for element in elements:
        if 'paragraph' in element:
            for run in element['paragraph']['elements']:
                if 'textRun' in run:
                    text += run['textRun']['content']
        elif 'table' in element:
            for row in element['table']['tableRows']:
                for cell in row['tableCells']:
                    text += extract_text(cell['content'])
        elif 'tableOfContents' in element:
            text += extract_text(element['tableOfContents']['content'])
    return text
