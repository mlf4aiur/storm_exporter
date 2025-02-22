#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import logging
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from prometheus_client import start_http_server, Gauge


# TOPOLOGY/SUMMARY METRICS
STORM_TOPOLOGY_UPTIME_SECONDS = Gauge('storm_topology_uptime_seconds','Shows how long the topology is running in seconds',['topology_name', 'topology_id'])
STORM_TOPOLOGY_TASKS_TOTAL = Gauge('storm_topology_tasks_total','Total number of tasks for this topology',['topology_name', 'topology_id'])
STORM_TOPOLOGY_WORKERS_TOTAL = Gauge('storm_topology_workers_total','Number of workers used for this topology',['topology_name', 'topology_id'])
STORM_TOPOLOGY_EXECUTORS_TOTAL = Gauge('storm_topology_executors_total','Number of executors used for this topology',['topology_name', 'topology_id'])
STORM_TOPOLOGY_REPLICATION_COUNT = Gauge('storm_topology_replication_count','Number of nimbus hosts on which this topology code is replicated',['topology_name', 'topology_id'])
STORM_TOPOLOGY_REQUESTED_MEM_ON_HEAP = Gauge('storm_topology_requested_mem_on_heap','Requested On-Heap Memory by User (MB)',['topology_name', 'topology_id'])
STORM_TOPOLOGY_REQUESTED_MEM_OFF_HEAP = Gauge('storm_topology_requested_mem_off_heap','Requested Off-Heap Memory by User (MB)',['topology_name', 'topology_id'])
STORM_TOPOLOGY_REQUESTED_TOTAL_MEM = Gauge('storm_topology_requested_total_mem','Requested Total Memory by User (MB)',['topology_name', 'topology_id'])
STORM_TOPOLOGY_REQUESTED_CPU = Gauge('storm_topology_requested_cpu','Requested CPU by User (%)',['topology_name', 'topology_id'])
STORM_TOPOLOGY_ASSIGNED_MEM_ON_HEAP = Gauge('storm_topology_assigned_mem_on_heap','Assigned On-Heap Memory by Scheduler (MB)',['topology_name', 'topology_id'])
STORM_TOPOLOGY_ASSIGNED_MEM_OFF_HEAP = Gauge('storm_topology_assigned_mem_off_heap','Assigned Off-Heap Memory by Scheduler (MB)',['topology_name', 'topology_id'])
STORM_TOPOLOGY_ASSIGNED_TOTAL_MEM = Gauge('storm_topology_assigned_total_mem','Assigned Total Memory by Scheduler (MB)',['topology_name', 'topology_id'])
STORM_TOPOLOGY_ASSIGNED_CPU = Gauge('storm_topology_assigned_cpu','Assigned CPU by Scheduler (%)',['topology_name', 'topology_id'])

# TOPOLOGY/STATS METRICS:
STORM_TOPOLOGY_STATS_TRANSFERRED = Gauge('storm_topology_stats_transferred','Number messages transferred in given window',['topology_name', 'topology_id','window'])
STORM_TOPOLOGY_STATS_EMITTED = Gauge('storm_topology_stats_emitted','Number of messages emitted in given window',['topology_name', 'topology_id','window'])
STORM_TOPOLOGY_STATS_COMPLETE_LATENCY = Gauge('storm_topology_stats_complete_latency','Total latency for processing the message',['topology_name', 'topology_id','window'])
STORM_TOPOLOGY_STATS_ACKED = Gauge('storm_topology_stats_acked','Number of messages acked in given window',['topology_name', 'topology_id','window'])
STORM_TOPOLOGY_STATS_FAILED = Gauge('storm_topology_stats_failed','Number of messages failed in given window',['topology_name', 'topology_id','window'])

# TOPOLOGY/ID SPOUT METRICS:
STORM_TOPOLOGY_SPOUTS_EXECUTORS = Gauge('storm_topology_spouts_executors','Number of executors for the spout',['topology_name', 'topology_id', 'spout_id'])
STORM_TOPOLOGY_SPOUTS_EMITTED = Gauge('storm_topology_spouts_emitted','Number of messages emitted in given window',['topology_name', 'topology_id', 'spout_id'])
STORM_TOPOLOGY_SPOUTS_COMPLETE_LATENCY = Gauge('storm_topology_spouts_complete_latency','Total latency for processing the message',['topology_name', 'topology_id', 'spout_id'])
STORM_TOPOLOGY_SPOUTS_TRANSFERRED = Gauge('storm_topology_spouts_transferred','Total number of messages transferred in given window',['topology_name', 'topology_id', 'spout_id'])
STORM_TOPOLOGY_SPOUTS_TASKS = Gauge('storm_topology_spouts_tasks','Total number of tasks for the spout',['topology_name', 'topology_id', 'spout_id'])
STORM_TOPOLOGY_SPOUTS_ACKED = Gauge('storm_topology_spouts_acked','Number of messages acked',['topology_name', 'topology_id', 'spout_id'])
STORM_TOPOLOGY_SPOUTS_FAILED = Gauge('storm_topology_spouts_failed','Number of messages failed',['topology_name', 'topology_id', 'spout_id'])

# TOPOLOGY/ID BOLT METRICS:
STORM_TOPOLOGY_BOLTS_PROCESS_LATENCY = Gauge('storm_topology_bolts_process_latency','Average time of the bolt to ack a message after it was received',['topology_name', 'topology_id', 'bolt_id'])
STORM_TOPOLOGY_BOLTS_CAPACITY = Gauge('storm_topology_bolts_capacity','This value indicates number of messages executed * average execute latency / time window',['topology_name', 'topology_id', 'bolt_id'])
STORM_TOPOLOGY_BOLTS_EXECUTE_LATENCY = Gauge('storm_topology_bolts_execute_latency','Average time to run the execute method of the bolt',['topology_name', 'topology_id', 'bolt_id'])
STORM_TOPOLOGY_BOLTS_EXECUTORS = Gauge('storm_topology_bolts_executors','Number of executor tasks in the bolt component',['topology_name', 'topology_id', 'bolt_id'])
STORM_TOPOLOGY_BOLTS_TASKS = Gauge('storm_topology_bolts_tasks','Number of instances of bolt',['topology_name', 'topology_id', 'bolt_id'])
STORM_TOPOLOGY_BOLTS_ACKED = Gauge('storm_topology_bolts_acked','Number of tuples acked by the bolt',['topology_name', 'topology_id', 'bolt_id'])
STORM_TOPOLOGY_BOLTS_FAILED = Gauge('storm_topology_bolts_failed','Number of tuples failed by the bolt',['topology_name', 'topology_id', 'bolt_id'])
STORM_TOPOLOGY_BOLTS_EMITTED = Gauge('storm_topology_bolts_emitted','of tuples emitted by the bolt',['topology_name', 'topology_id', 'bolt_id'])


def get_metric(metric):
    """Ensure metric values are valid for Prometheus."""
    if metric in (None, "N/A"):
        return 0
    else:
        return metric


def update_stats_metrics(stat, topology_name, topology_id):
    window = stat.get('window', 'N/A')

    STORM_TOPOLOGY_STATS_TRANSFERRED.labels(topology_name, topology_id, window).set(get_metric(stat.get('transferred')))
    STORM_TOPOLOGY_STATS_EMITTED.labels(topology_name, topology_id, window).set(get_metric(stat.get('emitted')))
    STORM_TOPOLOGY_STATS_COMPLETE_LATENCY.labels(topology_name, topology_id, window).set(get_metric(stat.get('completeLatency')))
    STORM_TOPOLOGY_STATS_ACKED.labels(topology_name, topology_id, window).set(get_metric(stat.get('acked')))
    STORM_TOPOLOGY_STATS_FAILED.labels(topology_name, topology_id, window).set(get_metric(stat.get('failed')))


def update_spout_metrics(spout, topology_name, topology_id):
    spout_id = spout.get('spoutId', 'N/A')

    STORM_TOPOLOGY_SPOUTS_EXECUTORS.labels(topology_name, topology_id, spout_id).set(get_metric(spout.get('executors')))
    STORM_TOPOLOGY_SPOUTS_EMITTED.labels(topology_name, topology_id, spout_id).set(get_metric(spout.get('emitted')))
    STORM_TOPOLOGY_SPOUTS_COMPLETE_LATENCY.labels(topology_name, topology_id, spout_id).set(get_metric(spout.get('completeLatency')))
    STORM_TOPOLOGY_SPOUTS_TRANSFERRED.labels(topology_name, topology_id, spout_id).set(get_metric(spout.get('transferred')))
    STORM_TOPOLOGY_SPOUTS_TASKS.labels(topology_name, topology_id, spout_id).set(get_metric(spout.get('tasks')))
    STORM_TOPOLOGY_SPOUTS_ACKED.labels(topology_name, topology_id, spout_id).set(get_metric(spout.get('acked')))
    STORM_TOPOLOGY_SPOUTS_FAILED.labels(topology_name, topology_id, spout_id).set(get_metric(spout.get('failed')))


def update_bolt_metrics(bolt, topology_name, topology_id):
    bolt_id = bolt.get('boltId', 'N/A')

    STORM_TOPOLOGY_BOLTS_PROCESS_LATENCY.labels(topology_name, topology_id, bolt_id).set(get_metric(bolt.get('processLatency')))
    STORM_TOPOLOGY_BOLTS_CAPACITY.labels(topology_name, topology_id, bolt_id).set(get_metric(bolt.get('capacity')))
    STORM_TOPOLOGY_BOLTS_EXECUTE_LATENCY.labels(topology_name, topology_id, bolt_id).set(get_metric(bolt.get('executeLatency')))
    STORM_TOPOLOGY_BOLTS_EXECUTORS.labels(topology_name, topology_id, bolt_id).set(get_metric(bolt.get('executors')))
    STORM_TOPOLOGY_BOLTS_TASKS.labels(topology_name, topology_id, bolt_id).set(get_metric(bolt.get('tasks')))
    STORM_TOPOLOGY_BOLTS_ACKED.labels(topology_name, topology_id, bolt_id).set(get_metric(bolt.get('acked')))
    STORM_TOPOLOGY_BOLTS_FAILED.labels(topology_name, topology_id, bolt_id).set(get_metric(bolt.get('failed')))
    STORM_TOPOLOGY_BOLTS_EMITTED.labels(topology_name, topology_id, bolt_id).set(get_metric(bolt.get('emitted')))


def update_topology_metrics(topology):
    topology_name = topology.get('name', 'N/A')
    topology_id = topology.get('id', 'N/A')

    for stat in topology.get('topologyStats', []):
        update_stats_metrics(stat, topology_name, topology_id)
    for spout in topology.get('spouts', []):
        update_spout_metrics(spout, topology_name, topology_id)
    for bolt in topology.get('bolts', []):
        update_bolt_metrics(bolt, topology_name, topology_id)


def collect_topology_summary_metrics(topology_summary, storm_ui_host):
    topology_name = topology_summary.get('name', 'N/A')
    topology_id = topology_summary.get('id', 'N/A')

    STORM_TOPOLOGY_UPTIME_SECONDS.labels(topology_name, topology_id).set(get_metric(topology_summary.get('uptimeSeconds')))
    STORM_TOPOLOGY_TASKS_TOTAL.labels(topology_name, topology_id).set(get_metric(topology_summary.get('tasksTotal')))
    STORM_TOPOLOGY_WORKERS_TOTAL.labels(topology_name, topology_id).set(get_metric(topology_summary.get('workersTotal')))
    STORM_TOPOLOGY_EXECUTORS_TOTAL.labels(topology_name, topology_id).set(get_metric(topology_summary.get('executorsTotal')))
    STORM_TOPOLOGY_REPLICATION_COUNT.labels(topology_name, topology_id).set(get_metric(topology_summary.get('replicationCount')))
    STORM_TOPOLOGY_REQUESTED_MEM_ON_HEAP.labels(topology_name, topology_id).set(get_metric(topology_summary.get('requestedMemOnHeap')))
    STORM_TOPOLOGY_REQUESTED_MEM_OFF_HEAP.labels(topology_name, topology_id).set(get_metric(topology_summary.get('requestedMemOffHeap')))
    STORM_TOPOLOGY_REQUESTED_TOTAL_MEM.labels(topology_name, topology_id).set(get_metric(topology_summary.get('requestedTotalMem')))
    STORM_TOPOLOGY_REQUESTED_CPU.labels(topology_name, topology_id).set(get_metric(topology_summary.get('requestedCpu')))
    STORM_TOPOLOGY_ASSIGNED_MEM_ON_HEAP.labels(topology_name, topology_id).set(get_metric(topology_summary.get('assignedMemOnHeap')))
    STORM_TOPOLOGY_ASSIGNED_MEM_OFF_HEAP.labels(topology_name, topology_id).set(get_metric(topology_summary.get('assignedMemOffHeap')))
    STORM_TOPOLOGY_ASSIGNED_TOTAL_MEM.labels(topology_name, topology_id).set(get_metric(topology_summary.get('assignedTotalMem')))
    STORM_TOPOLOGY_ASSIGNED_CPU.labels(topology_name, topology_id).set(get_metric(topology_summary.get('assignedCpu')))

    try:
        logging.info(f"Fetching detailed metrics for topology {topology_name}")
        response = requests.get(f'http://{storm_ui_host}/api/v1/topology/{topology_id}', timeout=5)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        if not content_type or 'application/json' not in content_type:
            logging.error(f"Invalid response format from Storm UI for topology {topology_id}")
            return

        try:
            topology_data = response.json()
            update_topology_metrics(topology_data)
        except ValueError:
            logging.error(f"Failed to parse JSON response for topology {topology_id}")
    except requests.exceptions.Timeout:
        logging.error(f"Timeout fetching topology {topology_id} details")
    except requests.RequestException as e:
        logging.error(f"Error fetching topology {topology_id} details: {e}")


def collect_all_topologies_metrics(storm_ui_host):
    try:
        response = requests.get(f'http://{storm_ui_host}/api/v1/topology/summary', timeout=5)
        response.raise_for_status()
        logging.info("Fetched topology summary successfully")

        for topology in response.json().get('topologies', []):
            collect_topology_summary_metrics(topology, storm_ui_host)
    except requests.exceptions.Timeout:
        logging.error("Timeout fetching topology summary")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error while fetching topology summary: {http_err}")
    except requests.RequestException as e:
        logging.error(f"Error fetching topology summary: {e}")


def main():
    parser = argparse.ArgumentParser(description='Storm Metrics Exporter')

    parser.add_argument(
        '--storm-ui-host',
        default=os.environ.get('STORM_UI_HOST', 'localhost'),
        help='Storm UI host')
    parser.add_argument(
        '--exporter-http-port',
        type=int,
        default=int(os.environ.get('EXPORTER_HTTP_PORT', 9800)),
        help='HTTP port for Prometheus exporter')
    parser.add_argument(
        '--refresh-rate', type=int,
        default=int(os.environ.get('REFRESH_RATE', 30)),
        help='Metrics refresh rate in seconds')
    parser.add_argument(
        '--log-level',
        default=os.environ.get('LOG_LEVEL', 'INFO'),
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info(f"Starting Storm Metrics Exporter on port {args.exporter_http_port}, polling {args.storm_ui_host} every {args.refresh_rate} seconds")

    try:
        start_http_server(args.exporter_http_port)
    except Exception as e:
        logging.error(f"Failed to start HTTP server on port {args.exporter_http_port}: {e}")
        return

    scheduler = BlockingScheduler()
    scheduler.add_job(
        collect_all_topologies_metrics,
        'interval',
        seconds=args.refresh_rate,
        args=[args.storm_ui_host],  # Pass the arguments to the function
        max_instances=1,
        coalesce=True)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Stopping Storm Metrics Exporter...")


if __name__ == '__main__':
    main()
