# generate SERVER CSR
openssl req -newkey rsa:2048 -nodes -keyout server.key  -out server.csr -subj "/C=CN/ST=SH/L=SH/O=FDU/OU=CS/CN=SERVER/emailAddress=312013477@qq.com"
# sign CSR 2 CRT
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt