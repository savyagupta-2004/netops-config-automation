FROM frrouting/frr:latest

RUN apk add --no-cache openssh iproute2 && \
    mkdir -p /var/run/sshd && \
    echo 'root:frrlab123' | chpasswd && \
    sed -i 's/#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    ssh-keygen -A

COPY daemons /etc/frr/daemons
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
