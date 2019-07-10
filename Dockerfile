FROM python:3
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .
EXPOSE 5000
RUN pip install -r requirements.txt
RUN export FLASK_APP=flaskr
RUN export FLASK_ENV=development
CMD ["python", "app.py"]