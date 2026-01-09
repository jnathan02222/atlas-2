# Deploying Atlas

## Frontend

Frontend deployment is handled automatically by Vercel. All you have to do is push to main.

If I chose to switch though it should be relatively portable, we just need to build
the static files and set up the proxy to the backend API.

## Backend

We use several [Docker](https://docs.docker.com/) containers to manage the backend
and streamline deployment. For the most part, all you have to do is spin up
a VM, pull this repo and run (in this directory):

```bash
docker compose up
```

Then, there are typically various annoying networking things to do:

1. Open up port 80 and 443 to allow access through the open internet.
2. Obtain a permanent IP for the VM.
3. Point your domain to this IP.
4. Run [Certbot](https://certbot.eff.org/) (bundled) with the Nginx container

```bash
docker exec -t -i deploy-nginx-1 /bin/bash

# Inside the container bash:
certbot --nginx

# renewal cron job
echo "0 0,12 * * * root /opt/certbot/bin/python -c 'import random; import time; time.sleep(random.random() * 3600)' && sudo certbot renew -q" | sudo tee -a /etc/crontab > /dev/null

exit
```

5. Cry after doing so much manual labour in an industry built on automation.

### Nginx

[Nginx](https://nginx.org/) is a load balancer / reverse proxy that
sits in front of the backend server.

To build the container that has it, run the following in `/nginx`.

```bash
docker buildx build -t atlas-2-nginx --platform linux/amd64,linux/arm64 .

docker tag atlas-2-nginx jnathan02222/atlas-2-nginx

docker push jnathan02222/atlas-2-nginx

```

In the future all builds will probably be automated through CI.
