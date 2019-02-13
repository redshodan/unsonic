#!/usr/bin/env python3

import os
from hashlib import md5
import tempfile
import argparse
from urllib import request
from urllib.error import URLError
from lxml import etree
from lxml.etree import XMLSyntaxError


def main():
    parser = argparse.ArgumentParser(description='Make API calls to Unsonic.')
    parser.add_argument('endpoint', type=str, nargs='?', default="ping",
                        help='API endpoint to talk to')
    parser.add_argument('params', type=str, nargs='*',
                        help='Parameters for the endpoint')
    parser.add_argument('-s', '--shares', action='store_true', default=False,
                        help='Use the /shares/ endpoints.')
    parser.add_argument('-t', '--tls', action='store_true', default=False,
                        help='Use TLS/HTTPS')
    parser.add_argument('-H', '--host', default="0.0.0.0",
                        help='Use the given host. Defaults to "0.0.0.0"')
    parser.add_argument('-P', '--port', default="6543",
                        help='Use the given port. Defaults to "6543"')
    parser.add_argument('-a', '--admin', action='store_true', default=False,
                        help='Use admin user')
    parser.add_argument('-u', '--user', default="test",
                        help='Use the given user. Defaults to "test"')
    parser.add_argument('-p', '--password', default="test",
                        help='Use the given password. Defaults to "test"')
    parser.add_argument('-S', '--salt', default="12345",
                        help='Use the given salt. Defaults to "12345"')

    args = parser.parse_args()

    if ((args.user and not args.password) or
          (not args.user and args.password)):
        parser.error("Must supply both --user and --password")

    if args.shares:
        args.root = "shares"
    else:
        args.root = "rest"
        args.endpoint = args.endpoint + ".view"

    user = args.user
    password = args.password
    salt = args.salt

    if args.admin:
        user = "admin"
        password = "admin"

    if args.tls:
        scheme = "https"
    else:
        scheme = "http"

    h = md5()
    h.update(password.encode("utf-8"))
    h.update(salt.encode("utf-8"))

    auth = f"u={user}&t={h.hexdigest()}&s={salt}"
    url = (f"{scheme}://{args.host}:{args.port}/" +
           f"{args.root}/{args.endpoint}?{auth}" +
           f"&{'&'.join(args.params)}")

    print(f"--> {url}")

    xsd = open("test/xsd/unsonic-subsonic-api.xsd").read().encode("utf-8")
    schema_root = etree.XML(xsd)
    schema = etree.XMLSchema(schema_root)
    parser = etree.XMLParser(schema = schema)

    try:
        resp = request.urlopen(url)
        data = resp.read()
        root = etree.fromstring(data, parser)
        print(f"<-- {etree.tostring(root, pretty_print=True).decode('utf-8')}")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt!")
    except URLError as e:
        print(str(e))
    except XMLSyntaxError as e:
        root = etree.fromstring(data, etree.XMLParser())
        print(f"<-- {etree.tostring(root, pretty_print=True).decode('utf-8')}")
        print(str(e))


if __name__ == "__main__":
    main()
