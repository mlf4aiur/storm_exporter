#!/usr/bin/env bash

# Function to wait for a service to become available using TCP connection
wait_for_service() {
  local host=$1
  local port=$2
  local name=$3

  echo "Waiting for $name ($host:$port)..."

  while ! (echo > "/dev/tcp/$host/$port") 2>/dev/null; do
    sleep 1
  done

  echo "$name is ready."
}

# Wait for Nimbus service to be available on port 6627 (non-HTTP)
wait_for_service "nimbus" 6627 "Storm Nimbus"

# Submit the Storm topology
echo "Submitting Storm topology..."
storm jar /storm/storm-starter-*.jar org.apache.storm.starter.WordCountTopology WordCountTopology
storm jar /storm/storm-starter-*.jar org.apache.storm.starter.RollingTopWords RollingTopWords
