"""Prometheus module."""

import logging

from typing import Dict, List

import requests

from wmflib.constants import ALL_DATACENTERS
from wmflib.exceptions import WmflibError
from wmflib.requests import http_session, TimeoutType

logger = logging.getLogger(__name__)


class PrometheusError(WmflibError):
    """Custom exception class for errors of this module."""


class PrometheusBase:
    """Base class to interact with Prometheus-like APIs."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self._http_session = http_session('.'.join((self.__module__, self.__class__.__name__)))

    def _query(self, url: str, params: Dict[str, str], timeout: TimeoutType) -> List[Dict]:
        """Perform a generic query.

        Arguments:
            url (str): the URL to query.
            params (dict): a dictionary of the GET parameters to pass to the URL.
            timeout (:py:data:`wmflib.requests.TimeoutType`): How many seconds to wait for prometheus to reply before
                giving up. This is passed directly to the requests library.

        Returns:
            list: returns an empty list if there are no results otherwise return a list of results of the form:
            ``{'metric': {}, 'value': [$timestamp, $value]}``.

        Raises:
            wmflib.prometheus.PrometheusError: on error

        """
        response = self._http_session.get(url, params=params, timeout=timeout)
        if response.status_code != requests.codes['ok']:
            raise PrometheusError(f'Unable to get metric: HTTP {response.status_code}: {response.text}')

        result = response.json()

        if result.get('status', 'error') == 'error':
            raise PrometheusError(f'Unable to get metric: {result.get("error", "unknown")}')

        return result['data']['result']


class Prometheus(PrometheusBase):
    """Class to interact with a Prometheus API instance.

    Examples:
        ::

            >>> from wmflib.prometheus import Prometheus
            >>> prometheus = Prometheus()

    """

    _prometheus_api: str = 'http://prometheus.svc.{site}.wmnet/{instance}/api/v1/query'

    def query(self, query: str, site: str, *, instance: str = 'ops', timeout: TimeoutType = 10.0) -> List[Dict]:
        """Perform a generic query.

        Examples:
            ::

                >>> results = prometheus.query('node_uname_info{instance=~"host1001:.*"}', 'eqiad', instance='global')
                >>> results = prometheus.query('node_memory_MemTotal_bytes{instance=~"host1001:.*"}', 'eqiad')

            The content of the last results will be something like::

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
            query (str): a prometheus query string.
            site (str): The site to use for queries. Must be one of
                :py:const:`wmflib.constants.ALL_DATACENTERS`
            instance (str, optional): The prometheus instance to query on the given site, see
                https://wikitech.wikimedia.org/wiki/Prometheus#Instances for the full list of available instances.
            timeout (:py:data:`wmflib.requests.TimeoutType`, optional): How many seconds to wait for prometheus to
                reply before giving up. This is passed directly to the requests library.

        Returns:
            list: returns an empty list if there are no results otherwise return a list of results of the form:
            ``{'metric': {}, 'value': [$timestamp, $value]}``.

        Raises:
            wmflib.prometheus.PrometheusError: on error

        """
        if site not in ALL_DATACENTERS:
            msg = f'site ({site}) must be one of wmflib.constants.ALL_DATACENTERS {ALL_DATACENTERS}'
            raise PrometheusError(msg)

        url = self._prometheus_api.format(site=site, instance=instance)
        params = {'query': query}
        return self._query(url, params, timeout)


class Thanos(PrometheusBase):
    """Class to interact with a Thanos API endpoint.

    Examples:
        ::

            >>> from wmflib.prometheus import Thanos
            >>> thanos = Thanos()

    """

    _thanos_api: str = 'https://thanos-query.discovery.wmnet/api/v1/query'

    def query(self, query: str, *, timeout: TimeoutType = 10.0) -> List[Dict]:
        """Perform a generic query.

        Examples:
            ::

                >>> results = thanos.query('node_memory_MemTotal_bytes{instance=~"host1001:.*"}')
                >>> results = thanos.query('node_uname_info{instance=~"host1001:.*"}')

            The content of the last results will be something like::

                [
                    {
                        'metric': {
                            '__name__': 'node_uname_info',
                            'cluster': 'management',
                            'domainname': '(none)',
                            'instance': 'host1001:9100',
                            'job': 'node',
                            'machine': 'x86_64',
                            'nodename': 'host1001',
                            'prometheus': 'ops',
                            'release': '5.10.0-11-amd64',
                            'site': 'eqiad',
                            'sysname': 'Linux',
                            'version': '#1 SMP Debian 5.10.92-2 (2022-02-28)'
                        },
                        'value': [1648898872.82, '1']
                    }
                ]

        Arguments:
            query (str): a prometheus query string.
            timeout (:py:data:`wmflib.requests.TimeoutType`, optional): How many seconds to wait for prometheus to
                reply before giving up. This is passed directly to the requests library.

        Returns:
            list: returns an empty list if there are no results otherwise return a list of results of the form:
            ``{'metric': {}, 'value': [$timestamp, $value]}``.

        Raises:
            wmflib.prometheus.PrometheusError: on error.

        """
        params = {'dedup': 'true', 'partial_response': 'false', 'query': query}
        return self._query(self._thanos_api, params, timeout)
