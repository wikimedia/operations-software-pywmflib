"""Prometheus module."""

import logging

from typing import Dict, List, Optional, Union

import requests

from wmflib.constants import ALL_DATACENTERS
from wmflib.exceptions import WmflibError
from wmflib.requests import http_session

logger = logging.getLogger(__name__)


class PrometheusError(WmflibError):
    """Custom exception class for errors of this module."""


class Prometheus:
    """Class to interact with the Prometheus server."""

    _prometheus_api: str = 'http://prometheus.svc.{site}.wmnet/ops/api/v1/query'

    def __init__(self) -> None:
        """Initialize the instance.

        Examples:
            ::

                >>> from wmflib.prometheus import Prometheus
                >>> prometheus = Prometheus()

        """
        self._http_session = http_session('.'.join((self.__module__, self.__class__.__name__)))

    def query(self, query: str, site: str, *, timeout: Optional[Union[float, int]] = 10) -> List[Dict]:
        """Perform a generic query.

        Examples:
            ::

                results = prometheus.query('node_memory_MemTotal_bytes{instance=~"host1001:.*"}', 'eqiad')

            The results will be something like::

                [
                    {
                        'metric': {
                            '__name__': 'node_memory_MemTotal_bytes',
                            'cluster': 'management',
                            'instance': 'host1001:9100',
                            'job': 'node',
                            'site': 'eqiad'
                        },
                        'value': [1636569623.988, '67225329664']
                    }
                ]

        Arguments:
            query (str): a prometheus query
            site (str): The site to use for queries. Must be one of
                :py:const:`wmflib.constants.ALL_DATACENTERS`
            timeout (float, int, None, optional): How many seconds to wait for the prometheus to
                send data before giving up, as a float or int. Alternatively None to indicate an
                infinite timeout.

        Returns:
            list: returns an empty list if there are no results otherwise return a list of
            results of the form: {'metric': {}, 'value': [$timestamp, $value]}

        Raises:
            wmflib.prometheus.PrometheusError: on error

        """
        if site not in ALL_DATACENTERS:
            msg = f'site ({site}) must be one of wmflib.constants.ALL_DATACENTERS {ALL_DATACENTERS}'
            raise PrometheusError(msg)

        url = self._prometheus_api.format(site=site)
        response = self._http_session.get(url, params={'query': query}, timeout=timeout)
        if response.status_code != requests.codes['ok']:
            msg = f'Unable to get metric: HTTP {response.status_code}: {response.text}'
            raise PrometheusError(msg)

        result = response.json()

        if result.get('status', 'error') == 'error':
            msg = f'Unable to get metric: {result.get("error", "unknown")}'
            raise PrometheusError(msg)

        return result['data']['result']
