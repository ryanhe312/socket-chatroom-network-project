# generate CA
openssl req -newkey rsa:2048 -nodes -keyout ca_rsa_private.pem -x509 -days 365 -out ca.crt -subj "/C=CN/ST=SH/L=SH/O=FDU/OU=CS/CN=CA/emailAddress=312013477@qq.com"
# generate SERVER CSR
openssl req -newkey rsa:2048 -nodes -keyout server_rsa_private.pem  -out server.csr -subj "/C=CN/ST=SH/L=SH/O=FDU/OU=CS/CN=SERVER/emailAddress=312013477@qq.com"
# sign CSR 2 CRT
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca_rsa_private.pem -CAcreateserial -out server.crt
# generate CLIENT CSR
openssl req -newkey rsa:2048 -nodes -keyout client_rsa_private.pem -out client.csr -subj "/C=CN/ST=SH/L=SH/O=FDU/OU=CS/CN=CLIENT/emailAddress=312013477@qq.com"
# sign CSR 2 CRT
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca_rsa_private.pem -CAcreateserial -out client.crt