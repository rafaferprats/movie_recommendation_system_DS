

FROM python:3.10-slim


RUN pip3 install --upgrade pip

# Create app directory
WORKDIR /app


COPY main.py /app/main.py




# Install the Python dependencies
RUN pip install pandas
RUN pip install numpy
RUN pip install scikit-learn==1.3.2
RUN pip install fastapi==0.104.1
RUN pip install uvicorn==0.24.0


# Bundle app source
COPY . .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=5000"]

