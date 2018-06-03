FROM nginx:latest

RUN rm -f /etc/nginx/conf.d/*
RUN mkdir -p /home/user

ADD nginx.conf /home/user/nginx.conf
ADD uwsgi_params /home/user/uwsgi_params
ADD init.sh /home/user/init.sh

ENV TZ Asia/Tokyo
RUN echo "--- Set timezone" && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

CMD /home/user/init.sh
