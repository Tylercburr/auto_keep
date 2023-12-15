import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import AuthorizedSession

# Load the credentials from the service account file
creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/photoslibrary.appendonly'])

# Delegate the domain-wide authority to the service account
delegated_creds = creds.with_subject('user@example.com') # replace 'user@example.com' with the email of the user account

# Build the service
service = build('drive', 'v3', credentials=delegated_creds)

# Get the note
note_id = 'note_id' # replace 'note_id' with the actual ID of the note
note = service.files().get(fileId=note_id).execute()

# Get the attachments
attachments = note.get('attachments', [])

# Specify the directory where you want to save the attachments
directory = 'Keeps/test'

# Download the attachments
for attachment in attachments:
   attachment_name = attachment['name']
   mime_type = attachment['mimeType']
   if mime_type.startswith('image/'):
       output_file = f"{directory}/{attachment_name}.{mime_type.split('/')[1]}"
       # Create the directory if it does not exist
       os.makedirs(os.path.dirname(output_file), exist_ok=True)
       # Download the attachment
       with open(output_file, 'wb') as f:
           request = service.files().get_media(fileId=attachment_name)
           downloader = MediaIoBaseDownload(f, request)
           done = False
           while done is False:
               status, done = downloader.next_chunk()
               print("Download %d%%." % int(status.progress() * 100))

# Build the Google Photos API service
photos_service = build('photoslibrary', 'v1', credentials=delegated_creds)

# Upload the images to Google Photos
for attachment in attachments:
   attachment_name = attachment['name']
   mime_type = attachment['mimeType']
   if mime_type.startswith('image/'):
       input_file = f"{directory}/{attachment_name}.{mime_type.split('/')[1]}"
       with open(input_file, 'rb') as f:
           image_contents = f.read()
       # Upload the image to Google Photos
       upload_token = photos_service.mediaItems().batchCreate(
           body={
               "newMediaItems": [{
                  "description": "Test photo",
                  "simpleMediaItem": {
                      "uploadToken": image_contents,
                      "fileName": attachment_name
                  }
               }]
           }
       ).execute()
       print("Uploaded image:", attachment_name)
