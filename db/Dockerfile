FROM mysql:5.6

ENV TZ Asia/Tokyo
RUN echo "--- Set timezone" && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata
