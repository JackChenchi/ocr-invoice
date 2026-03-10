import os
import sys
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import ocr_service
from app.services.invoice_extractor import InvoiceExtractor

conn = sqlite3.connect('ocr.db')
cursor = conn.cursor()

cursor.execute('SELECT id, image_url FROM ocr_results')
records = cursor.fetchall()

for record_id, image_url in records:
    print(f"\n{'='*60}")
    print(f"Processing ID {record_id}: {image_url}")
    print(f"{'='*60}")
    
    if image_url:
        full_path = os.path.join(os.path.dirname(__file__), image_url)
        
        if os.path.exists(full_path):
            try:
                result = ocr_service.process_image(full_path)
                print(f"Confidence: {result['confidence']:.2f}%")
                print(f"Text length: {len(result['text'])}")
                print(f"\nOCR Text:\n{result['text']}")
                
                extracted = InvoiceExtractor.extract_bank_receipt(result['text'])
                print(f"\nExtracted Data:")
                print(f"  Transaction Reference: {extracted.transaction_reference or 'N/A'}")
                print(f"  Amount: {extracted.amount or 'N/A'}")
                print(f"  Currency: {extracted.currency or 'N/A'}")
                
                cursor.execute('''
                    UPDATE ocr_results 
                    SET ocr_text = ?, confidence = ?, status = 'completed'
                    WHERE id = ?
                ''', (result['text'], result['confidence'], record_id))
                
                print(f"\n[Updated database for ID {record_id}]")
                
            except Exception as e:
                print(f"Error: {e}")
                cursor.execute('''
                    UPDATE ocr_results 
                    SET status = 'failed', error_msg = ?
                    WHERE id = ?
                ''', (str(e), record_id))
        else:
            print(f"File not found: {full_path}")
    else:
        print("No image URL in database")

conn.commit()
conn.close()
print("\n\nAll records processed!")
