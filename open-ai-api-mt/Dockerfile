FROM python:3.12

WORKDIR /home/quazi/Desktop/OfficeWorkRoot/bangla-tranlator-backend

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
