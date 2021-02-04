FROM python:3

LABEL MAINTAINER="Nyasha Stephen <info@notre-studio.co.uk>"

ENV GROUP_ID=1000 \
    USER_ID=1000

WORKDIR /var/www/

ADD . /var/www/
RUN pip install -r requirements.txt
RUN pip install gunicorn

RUN addgroup --gid $GROUP_ID www
RUN adduser --disabled-password -u $USER_ID --ingroup www www --shell /bin/sh
USER root
RUN chown www:www -R /var/www/
USER www

EXPOSE 5000

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "wsgi"]