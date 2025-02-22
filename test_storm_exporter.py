#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
import storm_exporter
import logging

class TestStormExporter(unittest.TestCase):
    @patch('storm_exporter.requests.get')
    def test_get_metric(self, mock_get):
        # Test valid metric: Ensure the function returns the same value for a valid input
        self.assertEqual(storm_exporter.get_metric(10), 10)

        # Test None value: Ensure None returns 0
        self.assertEqual(storm_exporter.get_metric(None), 0)

        # Test "N/A" value: Ensure "N/A" returns 0
        self.assertEqual(storm_exporter.get_metric("N/A"), 0)

        # Test float value: Ensure a float is correctly handled
        self.assertEqual(storm_exporter.get_metric(12.34), 12.34)

    @patch('storm_exporter.requests.get')
    def test_update_stats_metrics(self, mock_get):
        # Setup mock response for the stat values
        mock_stat = {
            'window': 'test_window',
            'transferred': 100,
            'emitted': 50,
            'completeLatency': 10,
            'acked': 90,
            'failed': 5
        }

        # Mock the Prometheus Gauge's 'labels' method for STORM_TOPOLOGY_STATS_TRANSFERRED
        with patch('storm_exporter.STORM_TOPOLOGY_STATS_TRANSFERRED.labels') as mock_labels:
            mock_gauge = MagicMock()  # Mock the Gauge object
            mock_labels.return_value = mock_gauge  # Return the mocked Gauge when 'labels' is called

            # Call the function to test
            storm_exporter.update_stats_metrics(mock_stat, 'topology_name', 'topology_id')

            # Verify that the 'set' method on the mock Gauge is called with the expected value (100)
            mock_gauge.set.assert_called_with(100)

    @patch('storm_exporter.requests.get')
    def test_collect_topology_summary_metrics(self, mock_get):
        # Mock topology summary response with sample data
        mock_topology_summary = {
            'name': 'topology_name',
            'id': 'topology_id',
            'uptimeSeconds': 100,
            'tasksTotal': 5,
            'workersTotal': 3,
            'executorsTotal': 2,
            'replicationCount': 1,
            'requestedMemOnHeap': 256,
            'requestedMemOffHeap': 128,
            'requestedTotalMem': 384,
            'requestedCpu': 50,
            'assignedMemOnHeap': 256,
            'assignedMemOffHeap': 128,
            'assignedTotalMem': 384,
            'assignedCpu': 50
        }

        # Mock the HTTP GET request to return the above mock topology summary
        mock_response = MagicMock()
        mock_response.json.return_value = {'topologies': [mock_topology_summary]}
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_get.return_value = mock_response

        # Mock Prometheus Gauges for uptime, tasks, and workers
        with patch('storm_exporter.STORM_TOPOLOGY_UPTIME_SECONDS.labels') as mock_uptime, \
            patch('storm_exporter.STORM_TOPOLOGY_TASKS_TOTAL.labels') as mock_tasks_total, \
            patch('storm_exporter.STORM_TOPOLOGY_WORKERS_TOTAL.labels') as mock_workers_total:

            # Simulate the return value of each 'labels' call to return a mock Gauge object
            mock_uptime_gauge = MagicMock()
            mock_tasks_total_gauge = MagicMock()
            mock_workers_total_gauge = MagicMock()

            # Assign the mock Gauge objects to the return values of labels
            mock_uptime.return_value = mock_uptime_gauge
            mock_tasks_total.return_value = mock_tasks_total_gauge
            mock_workers_total.return_value = mock_workers_total_gauge

            # Call the function under test to collect the metrics
            storm_exporter.collect_topology_summary_metrics(mock_topology_summary, 'localhost')

            # Verify that the 'set' method on each mock Gauge was called with the expected values
            mock_uptime_gauge.set.assert_called_with(100)
            mock_tasks_total_gauge.set.assert_called_with(5)
            mock_workers_total_gauge.set.assert_called_with(3)

    @patch('storm_exporter.requests.get')
    def test_collect_all_topologies_metrics(self, mock_get):
        # Mock topology summary response
        mock_topology_summary = {
            'name': 'topology_name',
            'id': 'topology_id',
            'uptimeSeconds': 100,
            'tasksTotal': 5,
            'workersTotal': 3,
            'executorsTotal': 2,
            'replicationCount': 1,
            'requestedMemOnHeap': 256,
            'requestedMemOffHeap': 128,
            'requestedTotalMem': 384,
            'requestedCpu': 50,
            'assignedMemOnHeap': 256,
            'assignedMemOffHeap': 128,
            'assignedTotalMem': 384,
            'assignedCpu': 50
        }

        # Mock the HTTP GET request to return the above mock topology summary
        mock_response = MagicMock()
        mock_response.json.return_value = {'topologies': [mock_topology_summary]}
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_get.return_value = mock_response

        with patch('storm_exporter.collect_topology_summary_metrics') as mock_collect_metrics:
            # Call the function to collect all topology metrics
            storm_exporter.collect_all_topologies_metrics('localhost')
            # Verify that the function 'collect_topology_summary_metrics' was called with the expected arguments
            mock_collect_metrics.assert_called_once_with(mock_topology_summary, 'localhost')

    @patch('storm_exporter.requests.get')
    def test_fetch_topology_details(self, mock_get):
        # Mock detailed topology data response
        mock_topology_data = {
            'topologyStats': [{'transferred': 100, 'emitted': 50, 'completeLatency': 10, 'acked': 90, 'failed': 5}],
            'spouts': [{'spoutId': 'spout_1', 'executors': 1, 'emitted': 100, 'completeLatency': 5}],
            'bolts': [{'boltId': 'bolt_1', 'processLatency': 2, 'capacity': 100, 'executeLatency': 1, 'executors': 1}]
        }

        # Mock the HTTP GET request to return the mock topology data
        mock_response = MagicMock()
        mock_response.json.return_value = mock_topology_data
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_get.return_value = mock_response

        with patch('storm_exporter.update_topology_metrics') as mock_update_metrics:
            # Call the function to fetch and update topology metrics
            storm_exporter.collect_topology_summary_metrics(mock_topology_data, 'localhost')
            # Verify that the 'update_topology_metrics' function was called with the expected data
            mock_update_metrics.assert_called_once_with(mock_topology_data)

if __name__ == '__main__':
    unittest.main()
