# デプロイ手順書

## 前提
- Amazon Linux 2023
- Docker / docker-compose インストール済
- ALB: HTTPS + OIDC (Entra ID) + EC2:8080 転送

## 手順

```bash
unzip chat_app_final.zip
cd chat_app_final

cp .env.sample .env
vi .env

docker compose up -d db
sleep 5

docker exec -i chat_app-db-1 psql -U postgres -d chat <<EOF
CREATE TABLE IF NOT EXISTS chat_logs (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,
  registered_at TIMESTAMPTZ DEFAULT now()
);
EOF

docker compose up -d app
```
