# Simple DNS server
this a simple DNS server based on: https://github.com/Rhynorater/rebindMultiA/tree/master
it either directs traffic to the host ip. or to a separate target ip depending on the domain.
the structure is as follows:
[{request_id}.][{target_server_ip}.target.]{host_ip}.ns.rebindmultia.com

`request_id` - is just any string string you want to make it easier to track your requests (this is optional).
`target_server_ip` - the server you would like to direct traffic to (this is also optional).
`host_ip` - the ip you are running the dnsserver on.

examples of valid domains:
`abcd.123.123.123.123.ns.rebindmultia.com`
`abcd.123.123.123.123.target.44.44.44.44.44.ns.rebindmultia.com`
`b255cc4d-5ab9-45a5-84a5-145207bf2f22.44.44.44.44.44.ns.rebindmultia.com`
