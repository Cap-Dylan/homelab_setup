# infra-stack

Docker Compose stack running on the ASUS Vivobook 16 (headless Ubuntu 24.04). 
Handles network-wide DNS filtering, metrics collection across all homelab nodes, 
and observability dashboards. Always-on, sleep permanently disabled.

## What's in the stack

| Service | Port | Role |
|---------|------|------|
| AdGuard Home | 53, 80 | Network-wide DNS sinkhole — blocks ads/trackers for every device on the network |
| Prometheus | 9090 | Metrics aggregation — scrapes Node Exporter on all four nodes every 15s, 30 day retention |
| Grafana | 3001 | Dashboards — Node Exporter Full (ID 1860), all nodes visible in one view |
| Node Exporter | host network | Local host metrics for the Vivobook itself |

## Monitored nodes

| Node | IP | Exporter |
|------|----|----------|
| Vivobook (this machine) | localhost:9100 | Docker container, `network_mode: host` |
| MSI GE76 | [TAILSCALE_IP]:9100 | systemd service |
| UGREEN NAS | [TAILSCALE_IP]:9100 | Docker container, `network_mode: host` |
| Lenovo (HA) | [LAN_IP]:9100 | Community add-on (loganmarchione/hassos-addons) |

## Setup

```bash
cd ~/homelab_setup/projects/infra-stack
docker compose up -d
```

AdGuard Home first-run wizard is at `http://localhost:3000` — after setup it moves to port 80.

Grafana default login is `admin` / password set via `GF_SECURITY_ADMIN_PASSWORD` env var 
in docker-compose.yml.

## DNS config

- Upstream: 1.1.1.1 (Cloudflare), 9.9.9.9 (Quad9)
- All devices on the network use the Vivobook as primary DNS
- Fallback: 1.1.1.1 direct (in case Vivobook is down)
- Set at the router level on the BE3600

## Prometheus scrape config

See `prometheus/prometheus.yml` for full target list. Scrape interval is 15s 
across all targets. Retention is 30 days.

## Gotchas

- AdGuard needs ports 53 and 80 — if something else is already bound to either,
  the container won't start. Check with `sudo ss -tuln | grep :53`
- Node Exporter must run with `network_mode: host` and `pid: host` to get 
  accurate system metrics — bridge networking gives you container metrics instead
- Grafana runs on 3001 (not default 3000) to avoid colliding with AdGuard's 
  first-run wizard
- HA's Node Exporter is a community add-on, not a native integration — install 
  via the add-on store using the loganmarchione/hassos-addons repo

## Host details

- **Machine**: ASUS Vivobook 16 (i5-1135G7, 8GB DDR4, 512GB NVMe)
- **OS**: Ubuntu 24.04 LTS headless
- **Sleep**: Permanently disabled (`systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target`)
- **Network**: Tailscale mesh + LAN
