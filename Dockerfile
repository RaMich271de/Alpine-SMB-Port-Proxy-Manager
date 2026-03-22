FROM alpine:3.21

RUN apk add --no-cache socat wsdd avahi avahi-tools dbus

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV DEVICE_IP=""
ENV DEVICE_PORT=""
ENV PROXY_NAME=""
ENV UUID=""

ENTRYPOINT ["/entrypoint.sh"]
