

FROM python:3.10-slim


RUN pip3 install --upgrade pip

# Create app directory
WORKDIR /app


COPY main.py /app/main.py




# Install the Python dependencies
RUN pip install pandas
RUN pip install numpy
RUN pip install scikit-learn==1.1.1
RUN pip install fastapi==0.104.1
RUN pip install uvicorn==0.24.0
RUN pip install matplotlib
RUN pip install pytest==7.4.4
RUN pip install httpx==0.26.0


# Bundle app source
COPY . .

EXPOSE $PORT
ENTRYPOINT ["uvicorn"]
CMD [ "main:app",  "--host", "0.0.0.0"]



