# import json
# from datetime import datetime
# from urllib import parse
#
# from src.app.batch.niconico_api_connector import NiconicoAPIConnector
# from src.app.batch.util import Util
# from src.app.util.gn_logger import GNLogger
#
# logger = GNLogger.get_logger(__name__)
#
#
# class NiconicoCommentPoster(NiconicoAPIConnector):
#     @staticmethod
#     def commented_at_string_to_unix_timestamp(d: str) -> int:
#         return int(datetime.strptime(d, "%Y/%m/%d").timestamp())
#
#     def post_comment(self, url: str, thread, vpos, mail, ticket, user_id, content, comment_num: int):
#         """post a comment
#
#         :param url: URL
#         :param thread: video thread number
#         :param vpos: position in video (e.g. '8:10')
#         :param mail: command (not mail address) (e.g. 'shita red big')
#         :param ticket: ticket to posting comment
#         :param user_id: user id who posts comment
#         :param content: comment content
#         :param comment_num: number of comments
#         :return: response for comment posting
#         """
#         Util.get_block_no(comment_num)
#         post_key = self.__get_post_key(block_no, thread)
#         param = {
#             "chat": {
#                 "thread": thread,
#                 "vpos": vpos,
#                 "mail": mail,
#                 "ticket": ticket,
#                 "user_id": user_id,
#                 "premium": 1,
#                 "content": content,
#                 "postkey": post_key
#             }
#         }
#         result = self.__access_to_api(url, is_post=True, post_data=param, is_json=True)
#         return json.loads(result)
#
#     def __get_post_key(self, block_no, thread) -> str:
#         """get post key to post a comment.
#
#         :param block_no: comment block no
#         :param thread: video thread id
#         :return: post key
#         """
#         result = self.__access_to_api(
#             "http://flapi.nicovideo.jp/api/getpostkey?thread={thread}&block_no={block_no}&device=1&version=1&version_sub=6".format(
#                 thread=thread, block_no=block_no))
#         result = parse.parse_qs(result.text)
#         return result['postkey'][0]
