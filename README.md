collectd-soap-service-python
========================

Python-based plugin to put `SOAP` service stats to [collectd](http://collectd.org)

Data captured includes:

 * Response time

[deniszh's Python ActiveMQ collectd plugin] (https://github.com/deniszh/collectd-activemq-python) - as inspiration.

Install
-------
 1. Place soap_info.py in /usr/lib/collectd/plugins/python
 2. Configure the plugin (see below).
 3. Restart collectd.

Configuration
-------------
Add the following to your collectd config

    <LoadPlugin python>
      Globals true
    </LoadPlugin>

    <Plugin python>
      ModulePath "/usr/lib/collectd/plugins/python"
      Import "soap_info"

      <Module soap_info>
        Endpoint "http://localhost:8080/service/test"
        RequestFile "test.xml"
      </Module>
    </Plugin>

Optional attributes can be set to find expected element and check it's value:

      <Module soap_info>
        Endpoint "http://localhost:8080/service/test"
        RequestFile "test.xml"
        ExpectedNode "responseCode"
        ExpectedValue "VALID"
      </Module>
_It will send POST request to http://localhost:8080/service/test from test.xml file, find element responseCode and check if at least one of found nodes has value 'VALID'_

Dependencies
------------
[Python-requests](http://www.python-requests.org/en/latest/) module is required. Please install it with `pip install requests` or use your package manager to install `python-requests` package or similar.

License
-------

[MIT](http://mit-license.org/)