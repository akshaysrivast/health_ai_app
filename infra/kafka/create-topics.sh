#!/bin/sh
set -e

echo "Waiting for Kafka to be ready..."
sleep 15

TOPICS_FILE="/topics/topics.txt"
BOOTSTRAP_SERVER="kafka:9092"

while IFS= read -r topic; do
  if [ -n "$topic" ]; then
    echo "Creating topic: $topic"
    kafka-topics --create \
      --if-not-exists \
      --bootstrap-server "$BOOTSTRAP_SERVER" \
      --replication-factor 1 \
      --partitions 3 \
      --topic "$topic"
  fi
done < "$TOPICS_FILE"

echo "Kafka topic initialization complete."
