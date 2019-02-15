#!/usr/bin/env python3

from hashlib import md5
import argparse
from urllib import request
from urllib.error import URLError
from urllib.parse import urlencode, quote_plus
import ssl

# Make lxml protocol verification optional
try:
    from lxml import etree
    from lxml.etree import XMLSyntaxError
except Exception:
    lxml = None

from . import Command



@Command.register
class Client(Command):
    NAME = "client"
    HELP = "A client for the Unsonic API"
    DESC = "A client for easily accessing the Unsonic API"
    DB_NEEDED = False


    def _initArgParser(self, parser):
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

    def run(self, args, config):
        super()._run()
        pargs = args.pserve_args

        print("args", args)
        print("pargs", pargs)

#     args = parser.parse_args()

#     if ((args.user and not args.password) or (not args.user and args.password)):
#         parser.error("Must supply both --user and --password")

#     if args.shares:
#         args.root = "shares"
#     else:
#         args.root = "rest"
#         args.endpoint = args.endpoint + ".view"

#     user = args.user
#     password = args.password
#     salt = args.salt

#     if args.admin:
#         user = "admin"
#         password = "admin"

#     if args.tls:
#         scheme = "https"
#     else:
#         scheme = "http"

#     h = md5()
#     h.update(password.encode("utf-8"))
#     h.update(salt.encode("utf-8"))

#     params = {a.split("=")[0]: a.split("=")[1] for a in args.params}
#     urlparms = urlencode(params, quote_via=quote_plus)
#     if len(urlparms):
#         urlparms = "&" + urlparms

#     auth = f"u={user}&t={h.hexdigest()}&s={salt}"
#     url = (f"{scheme}://{args.host}:{args.port}/" +
#            f"{args.root}/{args.endpoint}?{auth}" +
#            f"&v=1.14.0&c=12345{urlparms}")

#     print(f"--> {url}")

#     xsd = open("test/xsd/unsonic-subsonic-api.xsd").read().encode("utf-8")
#     schema_root = etree.XML(xsd)
#     schema = etree.XMLSchema(schema_root)
#     parser = etree.XMLParser(schema=schema)

#     try:
#         ctx = None
#         if args.tls:
#             ctx = ssl.create_default_context()
#             ctx.check_hostname = False
#             ctx.verify_mode = ssl.CERT_NONE
#         resp = request.urlopen(url, context=ctx)
#         data = resp.read()
#         root = etree.fromstring(data, parser)
#         print(f"<-- {etree.tostring(root, pretty_print=True).decode('utf-8')}")
#     except KeyboardInterrupt:
#         print("\nKeyboardInterrupt!")
#     except URLError as e:
#         print(str(e))
#     except lxml.etree.XMLSyntaxError as e:
#         root = etree.fromstring(data, etree.XMLParser())
#         print(f"<-- {etree.tostring(root, pretty_print=True).decode('utf-8')}")
#         print(str(e))


# if __name__ == "__main__":
#     main()
