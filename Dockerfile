FROM python:3
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD scrapr.py /
CMD [ "python", "./scrapr.py" ]
