# Grafana Silence

Automate periodic silence for Grafana < 8.4.

# Usage

1. Configure `config.yaml`
2. Run

```bash
docker run -v config.yaml:/app/config.yml bintangbahy/grafana-silence:latest
```