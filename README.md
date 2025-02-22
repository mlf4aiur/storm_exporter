# prometheus-storm-exporter
A prometheus exporter for apache storm metrics

Exports storm metrics exposed by the [storm-ui rest interface](https://storm.apache.org/releases/2.7.1/STORM-UI-REST-API.html)

## Quick Start
```
docker-compose up -d
```
- Login to http://localhost:3000/  (user:admin, password: admin)

## Usage
As python script:
```
storm_exporter.py --storm-ui-host <StormUI Host> --exporter-http-port <HTTP Port> --refresh-rate <Refresh Rate in Seconds> --log-level <Log Level>
```

As docker container:
```
docker build -t storm_exporter .
docker run --rm -e STORM_UI_HOST=storm-ui:8080 -e EXPORTER_HTTP_PORT=9800 -e REFRESH_RATE=30 -e LOG_LEVEL=INFO -p 9800:9800 --name storm_exp storm_exporter
```

## Building storm-starter
To build `storm-starter` using Maven and place the generated JAR file into the `./storm` folder, follow these steps:

```
git clone https://github.com/apache/storm-starter.git
cd storm-starter
mvn clean package -DskipTests
cp target/storm-starter-*.jar ./storm/
```

## Notes
- This project uses the [prometheus python_client library](https://github.com/prometheus/client_python)
- The docker-compose setup uses
	- [storm image](https://hub.docker.com/_/storm)
	- [zookeeper image](https://hub.docker.com/_/zookeeper/)
	- [prometheus image](https://hub.docker.com/r/prom/prometheus/)
	- [grafana image](https://hub.docker.com/r/grafana/grafana/)
