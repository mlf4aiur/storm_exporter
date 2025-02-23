#!/usr/bin/env ash

# Configuration variables
GRAFANA_HOST="grafana"
GRAFANA_PORT=3000
PROMETHEUS_HOST="prometheus"
PROMETHEUS_PORT=9090
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-admin}"
DASHBOARD_PATH="/grafana/apache-storm-dashboard.json"

# Function to wait for a service to become available using wget
wait_for_service() {
  local host=$1
  local port=$2
  local name=$3

  echo "Waiting for $name ($host:$port)..."

  # Check if the service is available
  while ! wget -q -O /dev/null "http://$host:$port"; do
    sleep 1
  done

  echo "$name is ready."
}

# Wait for Grafana and Prometheus
wait_for_service "$GRAFANA_HOST" "$GRAFANA_PORT" "Grafana"
wait_for_service "$PROMETHEUS_HOST" "$PROMETHEUS_PORT" "Prometheus"

# Add Prometheus as a Grafana data source
echo "Adding Prometheus as a Grafana data source..."
wget -q "http://$GRAFANA_HOST:$GRAFANA_PORT/api/datasources" \
     --header="Content-Type: application/json" \
     --header="Authorization: Basic $(echo -n "$GRAFANA_USER:$GRAFANA_PASSWORD" | base64)" \
     --post-data '{
       "name": "Prometheus",
       "type": "prometheus",
       "access": "proxy",
       "url": "http://prometheus:9090",
       "basicAuth": false
     }'

# Upload the dashboard JSON file
if [ -f "$DASHBOARD_PATH" ]; then
  echo "Uploading Apache Storm Dashboard..."

  # Read the dashboard JSON file and send it in the request
  DASHBOARD_JSON=$(cat "$DASHBOARD_PATH")

  wget -q "http://$GRAFANA_HOST:$GRAFANA_PORT/api/dashboards/db" \
       --header="Content-Type: application/json" \
       --header="Authorization: Basic $(echo -n "$GRAFANA_USER:$GRAFANA_PASSWORD" | base64)" \
       --post-data "{
  \"dashboard\": $DASHBOARD_JSON,
  \"overwrite\": true
}"

  echo "Dashboard uploaded successfully."
else
  echo "Error: Dashboard file '$DASHBOARD_PATH' not found."
  exit 1
fi
