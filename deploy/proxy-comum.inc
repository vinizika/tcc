# Cabeçalhos e tempos de espera comuns às rotas /api/ (incluído por nginx.prod.conf).
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto https;
# A pré-triagem pode esperar o Gemini por mais de um minuto; o backend admite
# 600 s, e o proxy espera pelo mesmo trabalho em vez de devolver 504 aos 60 s.
proxy_connect_timeout 10s;
proxy_send_timeout 660s;
proxy_read_timeout 660s;
