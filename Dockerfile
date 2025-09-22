FROM python:3.11
WORKDIR /actualization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /actualization
CMD ["python", "main.py"]