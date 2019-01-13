import re
import xml.etree.ElementTree as ET
from luqum.parser import parser as LQParser
from luqum.tree import (BaseOperation, OrOperation, AndOperation, SearchField,
                        Word, Phrase)
from sqlalchemy import func

from . import (Command, registerCmd, MissingParam, NotFound, positive_t,
               fillArtist, fillAlbum, fillTrack, folder_t)
from ...models import Artist, Album, Track
from ...log import log


QUERY_LABELS = ["artist:", "album:", "title:"]
QUERY_REGEX = \
r'(ARTIST:|artist:|ALBUM:|album:|TITLE:|title:)("[^"]+"|[^ ]+)[ ]*(AND|and|OR|or)*'


@registerCmd
class Search2(Command):
    name = "search2.view"
    param_defs = {
        "query": {"required": True},
        "artistCount": {"default": 20, "type": positive_t},
        "artistOffset": {"default": 0, "type": positive_t},
        "albumCount": {"default": 20, "type": positive_t},
        "albumOffset": {"default": 0, "type": positive_t},
        "songCount": {"default": 20, "type": positive_t},
        "songOffset": {"default": 0, "type": positive_t},
        "musicFolderId": {"type": folder_t},
        }
    dbsess = True


    def __init__(self, route, req, session=None):
        super().__init__(route, req, session)
        self.setParams()


    def setParams(self, search_param="searchResult2"):
        self.search_param = search_param


    def query(self, session, klass):
        if self.params["musicFolderId"]:
            return (session.query(klass).
                    filter(klass.lib_id == self.params["musicFolderId"]))
        else:
            return session.query(klass)


    def globQuery(self, query):
        if query.startswith("*"):
            query = f"%%{query[1:]}"
        if query.endswith("*"):
            query = f"{query[:-1]}%%"
        return query

    # This is reverse engineered from what dsub will send for queries.
    def parseComplexQuery(self, session, query):
        tree = LQParser.parse(query)
        print(query)
        print(repr(tree))
        # For handling queries like: Tool
        have_op = False

        def extend(iterable, item):
            if isinstance(item, list):
                iterable.extend(item)
            else:
                iterable.append(item)
            return iterable

        def walker(t):
            print("Walker top")
            # As far I can see, groups are superfluous for what is needed here
            if isinstance(t, Group):
                print("Group")
                if len(t.children) != 1:
                    raise Exception("Uh, too many group children???")
                return walker(t.children[0])
            elif isinstance(t, BaseOperation):
                print("BaseOperation")
                have_op = True
                results = []
                for c in t.children:
                    extend(results, walker(c))
                if isinstance(t, AndOperation):
                    print("AndOperation")
                    if None in results:
                        return None
                    else:
                        return results
                elif isinstance(t, OrOperation):
                    print("OrOperation")
                    for r in results:
                        if r is not None:
                            return [r for r in results if r]
                    else:
                        return None
                else:
                    raise MissingParam("Invalid operation: " + repr(t))
            elif isinstance(t, SearchField):
                print("SearchField")
                

            raise NotFound("No matching results found")

    # # This is reverse engineered from what dsub will send for queries.
    # def parseComplexQuery(self, session, query):
    #     arr = re.findall(QUERY_REGEX, query)
    #     if not arr:
    #         return None
    #     print("arr", arr)

    #     results = []
    #     for label, sub_query, op in arr:
    #         if label == "artist:":
    #             klass = Artist
    #             klass_label = Artist.name
    #             filler = fillArtist
    #             count = self.params["artistCount"]
    #             off = self.params["artistOffset"]
    #         elif label == "album:":
    #             klass = Album
    #             klass_label = Album.title
    #             filler = fillAlbum
    #             count = self.params["albumCount"]
    #             off = self.params["albumOffset"]
    #         elif label == "title:":
    #             klass = Track
    #             klass_label = Track.title
    #             filler = fillTrack
    #             count = self.params["songCount"]
    #             off = self.params["songOffset"]
    #         else:
    #             raise MissingParam(f"Invalid query label: {tokens[0]}")

    #         sub_query = sub_query.strip('"')
    #         sub_query = self.globQuery(sub_query)
    #         op = op.upper()

    #         sub_res = [[], op]
    #         results.append(sub_res)
    #         for row in self.query(session, klass). \
    #                        filter(klass_label.ilike(sub_query)). \
    #                        limit(count). \
    #                        offset(off):
    #             tag = filler(session, row)
    #             sub_res[0].append(tag)
    #         else:
    #             print("NONE FOUND")

    #     print("results", results)
    #     last_res = []
    #     for idx, pair in enumerate(results):
    #         res, op = pair
    #         print("last_res", last_res, "res", res)
    #         if op == "AND" and not (len(res) and len(last_res)):
    #             raise NotFound()
    #         elif op == "OR" and not (len(res) or len(last_res)):
    #             raise NotFound()
    #         # else ignore the trailing empty operator
    #         last_res = res

    #     # Got this far, we have a match!
    #     return [r for res, op in results for r in res]

    def handleReq(self, session):
        query = self.params["query"]
        ar_count = self.params["artistCount"]
        ar_off = self.params["artistOffset"]
        al_count = self.params["albumCount"]
        al_off = self.params["albumOffset"]
        tr_count = self.params["songCount"]
        tr_off = self.params["songOffset"]
        result = ET.Element(self.search_param)

        # Try the complex query first
        try:
            parsed_result = self.parseComplexQuery(session, query)
            print("parsed_result", parsed_result)
        except (MissingParam, NotFound) as e:
            raise e
        except Exception as e:
            log.error(f"Failed to parse search query: {query}",
                      exc_info=e)
            raise MissingParam("Invalid search query")

        if parsed_result is not None:
            for tag in parsed_result:
                result.append(tag)
            return self.makeResp(child=result)

        # Now just blast sub-string match queries
        if ar_count:
            for row in self.query(session, Artist). \
                           filter(Artist.name.ilike("%%%s%%" % query)). \
                           limit(ar_count). \
                           offset(ar_off):
                artist = fillArtist(session, row)
                result.append(artist)
        if al_count:
            for row in self.query(session, Album). \
                           filter(Album.title.ilike("%%%s%%" % query)). \
                           limit(al_count). \
                           offset(al_off):
                album = fillAlbum(session, row)
                result.append(album)
        if tr_count:
            for row in self.query(session, Track). \
                           filter(Track.title.ilike("%%%s%%" % query)). \
                           limit(tr_count). \
                           offset(tr_off):
                track = fillTrack(session, row)
                result.append(track)
        return self.makeResp(child=result)
