"""Prometheus module tests."""
import pytest

from wmflib.prometheus import Prometheus, PrometheusError, Thanos


def get_response_data(check='ok'):
    """Return mocked data based on the test."""
    json_data = {
        'status': 'success',
        'data': {
            'resultType': 'vector',
            'result': [{
                'metric': {},
                'value': [1553173538.378, '42.42']
            }]
        }
    }
    if check == 'empty_result':
        json_data['data']['result'] = []
    elif check == 'error':
        del json_data['data']
        json_data['status'] = 'error'
        json_data['error'] = 'Foobar error'

    return json_data


class TestPrometheus:
    """Test class for the Prometheus class."""

    def setup_method(self):
        """Setup the test environment."""
        # pylint: disable=attribute-defined-outside-init
        self.ops_uri = 'http://prometheus.svc.eqiad.wmnet/ops/api/v1/query'
        self.global_uri = 'http://prometheus.svc.eqiad.wmnet/global/api/v1/query'
        self.prometheus = Prometheus()

    def test_init(self):
        """It should initialise the instance."""
        assert isinstance(self.prometheus, Prometheus)

    def test_bad_site(self):
        """Test with a bad site parameter."""
        with pytest.raises(
                PrometheusError, match=r'site \(bad_site\) must be one of wmflib.constants.ALL_DATACENTERS'):
            self.prometheus.query('query_string', 'bad_site')

    def test_query_ok(self, requests_mock):
        """Check parsing a good request."""
        requests_mock.get(self.global_uri, json=get_response_data('ok'), status_code=200)
        assert 'value' in self.prometheus.query('query_string', 'eqiad', instance='global')[0]

    def test_query_not_ok(self, requests_mock):
        """Check we error on a fetch failure."""
        requests_mock.get(self.ops_uri, json=get_response_data('not_ok'), status_code=503)
        with pytest.raises(PrometheusError, match='Unable to get metric: HTTP 503'):
            self.prometheus.query('query_string', 'eqiad')

    def test_query_error(self, requests_mock):
        """Check handling an error in response data."""
        requests_mock.get(self.ops_uri, json=get_response_data('error'), status_code=200)
        with pytest.raises(PrometheusError, match='Unable to get metric: Foobar error'):
            self.prometheus.query('query_string', 'eqiad')

    def test_query_empty_result(self, requests_mock):
        """Test for en empty result."""
        requests_mock.get(self.ops_uri, json=get_response_data('empty_result'), status_code=200)
        assert not self.prometheus.query('query_string', 'eqiad')


class TestThanos:
    """Test class for the Prometheus class."""

    def setup_method(self):
        """Setup the test environment."""
        # pylint: disable=attribute-defined-outside-init
        self.uri = 'https://thanos-query.discovery.wmnet/api/v1/query'
        self.thanos = Thanos()

    def test_init(self):
        """It should initialise the instance."""
        assert isinstance(self.thanos, Thanos)

    def test_query_ok(self, requests_mock):
        """Check parsing a good request."""
        requests_mock.get(f'{self.uri}?dedup=true&partial_response=false&query=query_string',
                          json=get_response_data('ok'), status_code=200)
        assert 'value' in self.thanos.query('query_string')[0]
