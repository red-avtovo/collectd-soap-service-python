# collectd-soap-service-python
# ========================
#
# Python-based plugin to put SOAP-service validation stats to collectd
#
# https://github.com/deniszh/collectd-activemq-python - was used as inspiration

from xml.dom import minidom
import requests


class SOAPMonitor(object):
    def __init__(self, plugin_name='soap_info', endpoint='localhost', request_file="",
                 expected_node="", expected_value="",
                 verbose_logging=False):
        self.plugin_name = plugin_name
        self.endpoint = endpoint
        self.request_file = request_file
        self.expected_node = expected_node
        self.expected_value = expected_value
        self.verbose_logging = verbose_logging

    def log_verbose(self, msg):
        if not self.verbose_logging:
            return
        elif __name__ == '__main__':
            print msg
        else:
            collectd.info('%s plugin [verbose]: %s' % (self.plugin_name, msg))

    def configure_callback(self, conf):
        """Receive configuration block"""
        for node in conf.children:
            if node.key == 'Endpoint':
                self.endpoint = node.values[0]
            elif node.key == 'RequestFile':
                self.request_file = node.values[0]
            elif node.key == 'ExpectedNode':
                self.expected_node = node.values[0]
            elif node.key == 'ExpectedValue':
                self.expected_value = node.values[0]
            elif node.key == 'Verbose':
                self.verbose_logging = bool(node.values[0])
            else:
                collectd.warning('%s plugin: Unknown config key: %s.' % (self.plugin_name, node.key))
        self.log_verbose('Configured with endpoint=%s, request file=%s, expected node=%s' % (
            self.endpoint, self.request_file, self.expected_node))

    def dispatch_value(self, plugin_instance, value_type, instance, value):
        """Dispatch a value to collectd"""
        self.log_verbose('Sending value: %s.%s.%s=%s' % (self.plugin_name, plugin_instance, instance, value))
        if __name__ == "__main__":
            return
        val = collectd.Values()
        val.plugin = self.plugin_name
        val.plugin_instance = plugin_instance
        val.type = value_type
        val.type_instance = instance
        val.values = [value, ]

        val.dispatch()

    def fetch_metrics(self):
        """Connect to SOAP-service and return DOM object"""
        try:
            try:
                with open(self.request_file, 'r') as requestPost:
                    post_data = requestPost.read().replace('\n', '')
            except Exception:
                self.log_verbose('%s plugin: File %s not found' % (self.plugin_name, self.request_file))
                return

            if post_data:
                headers = {'Content-Type': 'application/xml'}
                post_request = requests.post(self.endpoint, data=post_data, headers=headers)
                if post_request.status_code != 200:
                    return
                latency = post_request.elapsed.microseconds / 1000
                dom = minidom.parseString(post_request.text)
        except Exception:
            self.log_verbose('%s plugin: No info received, offline node' % self.plugin_name)
            return

        if self.expected_node:
            found_nodes = dom.getElementsByTagName(self.expected_node)
            if found_nodes.length == 0:
                return
            if self.expected_value:
                value_found = None
                for node in found_nodes:
                    if node.firstChild.nodeValue == self.expected_value:
                        value_found = True
                if not value_found:
                    return

        gauges = []
        counters = []

        endpoint_code = self.endpoint.replace(".", "_").replace("//", "").replace("/", "_").replace(":", "_")

        gauges.append((endpoint_code, 'response_time', latency))
        counters.append((endpoint_code, 'response_time', latency))

        metrics = {
            'gauges': gauges,
            'counters': counters,
        }
        return metrics

    def read_callback(self):
        """Collectd read callback"""
        self.log_verbose('Read callback called')
        metrics = self.fetch_metrics()
        if metrics is None:
            self.log_verbose('No metrics returned.')
            return

        for gauge in metrics['gauges']:
            self.dispatch_value(gauge[0], 'gauge', gauge[1], gauge[2])

        for counter in metrics['counters']:
            self.dispatch_value(counter[0], 'counter', counter[1], counter[2])


if __name__ == "__main__":
    import argparse


    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('endpoint')
        parser.add_argument('requestFile')
        parser.add_argument('-n', '--expected-node', default="")
        parser.add_argument('-v', '--expected-value', default="")
        return parser.parse_args()


    args = parse_args()
    amq = SOAPMonitor(endpoint=args.endpoint, request_file=args.requestFile,
                      expected_node=args.expected_node, expected_value=args.expected_value,
                      verbose_logging=True)
    amq.read_callback()

else:
    import collectd

    amq = SOAPMonitor()
    # register callbacks
    collectd.register_config(amq.configure_callback)
    collectd.register_read(amq.read_callback)
