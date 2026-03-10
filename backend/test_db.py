from app.db.session import SessionLocal
from app.models.ocr import OCRResult, OCRStatus
from sqlalchemy import text

try:
    db = SessionLocal()
    # Test connection
    db.execute(text('SELECT 1'))
    print('Database connection successful')
    
    # Test insert
    ocr = OCRResult(file_name='test.jpg', file_size=100, status=OCRStatus.PENDING)
    db.add(ocr)
    db.commit()
    print('Database insert successful')
    db.close()
except Exception as e:
    print(f'Database Error: {e}')
