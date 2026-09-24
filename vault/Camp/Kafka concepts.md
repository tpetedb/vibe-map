---
title: "Kafka concepts"
date: 2026-09-18
tags: [tech, data]
generated: a241a8745ceb
---
# Kafka concepts

Kafka is a durable log that many programs write to and many programs read from, at their own speed. Reach for it when events have to reach several consumers that do not know about each other, when the reader may be down while the writer is not, or when the order of events per customer is part of the answer. The three words that carry the whole model are topic, partition and consumer group: a topic is the name, a partition is the ordered piece that gives you the ordering guarantee, and a group is how a team of consumers divides the partitions between them. This topic is concepts only, on purpose: the documented way to run either Kafka or Redpanda on a laptop needs Docker and several gigabytes, which is more than a twenty-minute exercise can ask for. And for an agent: if a question is answered by reading the same events twice from different places, you are looking at a log, not a queue.

**History.** Kafka's own introduction defines the pieces in order. "An event records the fact that 'something happened' in the world or in your business. It is also called record or message in the documentation." "Producers are those client applications that publish (write) events to Kafka, and consumers are those that subscribe to (read and process) these events." "Events are organized and durably stored in topics. Very simplified, a topic is similar to a folder in a filesystem, and the events are the files in that folder." The guarantee people actually build on is this one: "Events with the same event key (e.g., a customer or vehicle ID) are written to the same partition, and Kafka guarantees that any consumer of a given topic-partition will always read that partition's events in exactly the same order as they were written." Groups are the other half, from the consumer javadoc: "All consumer instances sharing the same group.id will be part of the same consumer group", "each partition is assigned to exactly one consumer in the group", and therefore "The number of total threads across all processes will be limited by the total number of partitions".

**Try in five minutes.** Count the partitions of a topic you use at work, then count its consumers. If the consumers outnumber the partitions, some of them are idle.

- Docs: [Source: LinkedIn, invitation to the Mountain View Kafka talk](https://www.linkedin.com/blog/engineering/archive/come-linkedin-hear-talk-about-kafka-our-open-source-distributed-pub-sub-messaging-system), [Apache Kafka, introduction and main concepts](https://kafka.apache.org/intro), [Apache Kafka, the KafkaConsumer javadoc on groups and offsets](https://kafka.apache.org/43/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html), [Source: Redpanda quickstart, which is Docker Compose and 4 GB of free memory](https://docs.redpanda.com/current/get-started/quick-start/)
- Unlocks: [[Ingestion, transformation, orchestration]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
