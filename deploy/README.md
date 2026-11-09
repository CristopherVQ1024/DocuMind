# Despliegue en la VM compartida con MoviFi

El Caddy de MoviFi es el único que publica 80 y 443. DocuMind no abre esos puertos: su contenedor `documind-web` entra a una red compartida `edge` y el Caddy le pasa el tráfico del subdominio.

## 0. Antes de empezar

- Disco: la VM tenía 1,2 GB libres de 9,7 GB. Las imágenes de DocuMind pesan unos 800 MB y construir Angular necesita más. Ampliar el disco en la consola de GCP (Compute Engine, Discos, editar tamaño a 20 GB) y luego en la VM:
  `sudo growpart /dev/sda 1 && sudo resize2fs /dev/sda1`
- Respaldo de MoviFi: `cd ~/movifi && ./deploy/respaldo.sh`.
- Subdominio nuevo en DuckDNS apuntando a la IP de la VM, por ejemplo `documind.duckdns.org`.
- Agregar ese dominio en Firebase, Authentication, Settings, Authorized domains.

## 1. Red compartida

```bash
docker network create edge
```

En `~/movifi/docker-compose.yml`, el servicio `web` entra también a `edge`:

```yaml
  web:
    networks: [default, edge]

networks:
  edge:
    external: true
```

## 2. Caddyfile de MoviFi

Agregar un bloque al final de `~/movifi/deploy/Caddyfile`, con el mismo formato que ya usa el archivo:

```
documind.duckdns.org {
    reverse_proxy documind-web:80 {
        flush_interval -1
    }
}
```

`flush_interval -1` hace que las respuestas en streaming lleguen token a token. Después: `cd ~/movifi && docker compose up -d --build web` y comprobar `curl https://movifi.duckdns.org/api/health`.

## 3. DocuMind

```bash
cd ~ && git clone https://github.com/CristopherVQ1024/DocuMind.git documind && cd documind
cp .env.example .env && nano .env      # GEMINI_API_KEY, FIREBASE_PROJECT_ID, CORS_ORIGINS=https://documind.duckdns.org
docker compose up -d --build
sleep 15 && curl https://documind.duckdns.org/api/health
```

No renombrar `~/documind`: compose nombra los volúmenes según la carpeta. No construir DocuMind y MoviFi a la vez.

Actualizar: `git pull && docker compose up -d --build`.
