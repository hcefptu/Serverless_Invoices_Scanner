import json
import boto3
import uuid

s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Invoices')

def lamba_handler(event, context):
    bucket_name = event['Records'][0]['bucket']['name']
    file_name = event['Records'][0]['object']['key']

    print(f"New file {file_name} is updated in {bucket_name} bucket")
    try:
        respone = textract_client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name  
                }
            }
        )

        detect_text = ""
        for item in respone['Blocks']:
            if item['BlockType'] == 'Line':
                detect_text += item['Text'] + " "
            
        invoice_id = str(uuid.uuid4())

        table.put_item(
            Item={
                'InvoiceId': invoice_id,
                'FileName': file_name,
                'RawText': detect_text
            }
        )
        return {
            'status_code': 200,
            'body': json.dump('Done!')
        }
    except Exception as e:
        print(f"Error: {str(e)}")