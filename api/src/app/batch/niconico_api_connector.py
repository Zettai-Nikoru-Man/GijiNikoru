import json
from datetime import datetime
from typing import Tuple
from urllib import parse
from xml.etree import ElementTree

import requests

from src.app.batch.comments import Comments
from src.app.batch.util import Util
from src.app.batch.video_api_info import VideoAPIInfo
from src.app.batch.video_info import VideoInfo
from src.app.config.constants import Constants
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class NiconicoAPIConnector:
    def __init__(self):
        self.http_session = requests.Session()  # this session has cookie
        self.login()  # login for following api access

    def get_video_api_info(self, video_id: str):
        result = self.access_to_api("http://flapi.nicovideo.jp/api/getflv/" + video_id)
        result = parse.parse_qs(result.text)
        return VideoAPIInfo(video_id, int(result['thread_id'][0]), result['user_id'][0], result['ms'][0],
                            result['userkey'][0])

    def get_comments(self, video_id: str, commented_at: str = None, commented_point: str = None):
        video_api_info = self.get_video_api_info(video_id)
        params_and_condition = self.get_params_for_comment(video_api_info, commented_at, commented_point)
        result = self.access_to_api(video_api_info.comment_server_url_json, is_post=True,
                                    post_data=params_and_condition["params"], is_json=True)
        return Comments(params_and_condition["condition"], result.json())

    def post_comment(self, url: str, thread, vpos, mail, ticket, user_id, content, post_key):
        param = {
            "chat": {
                "thread": thread,
                "vpos": vpos,
                "mail": mail,
                "ticket": ticket,
                "user_id": user_id,
                "premium": 1,
                "content": content,
                "postkey": post_key
            }
        }
        result = self.access_to_api(url, is_post=True, post_data=param, is_json=True)
        return json.loads(result)

    def get_commented_point(self, video_info: VideoInfo, commented_point):
        if not commented_point:
            return "0-" + Util.get_minute_from_video_time_point(video_info.length)
        commented_minute = Util.get_minute_from_video_time_point(commented_point)
        if commented_minute is None:
            return "0-100"
        return "{}-{}".format(max(0, int(commented_minute) - 1), int(commented_minute) + 1)

    def get_video_info(self, video_id: str) -> VideoInfo:
        api_response = self.access_to_api("http://ext.nicovideo.jp/api/getthumbinfo/" + video_id)
        if api_response.status_code != 200:
            raise Exception('failed to get video info from niconico API. video_id -> {}'.format(video_id))
        root = ElementTree.fromstring(api_response.content)
        data = {child.tag: child.text for child in root[0]}
        return VideoInfo(data)

    def get_params_for_comment(self, video_api_info: VideoAPIInfo, commented_at: str, commented_point: str):
        """make parameters to get comment

        :param video_api_info:
        :param commented_at:
        :param commented_point:
        :return:
        """
        # TODO: delete unused code

        # now we don't support collecting past comment data
        # wayback_key = self.get_wayback_key(video_api_info.thread_id)

        if commented_at is None:
            commented_at = int(datetime.now().timestamp())
        else:
            # 指定がある場合は指定時刻から1日後
            commented_at = self.commented_at_string_to_unix_timestamp(commented_at) + 60 * 60 * 24

        video_info = self.get_video_info(video_api_info.video_id)
        commented_point = self.get_commented_point(video_info, commented_point)
        condition = {
            "video_info": video_info,
            "commented_point": commented_point,
            "commented_at": commented_at,
        }

        params = [
            {
                "thread": {
                    "language": 0,
                    "nicoru": 1,
                    "scores": 1,
                    "thread": str(video_api_info.thread_id),
                    "user_id": video_api_info.user_id,
                    "userkey": video_api_info.user_key,
                    "version": '20090904',
                    # "waybackkey": wayback_key,
                    "with_global": 1,
                    # "when": commented_at,
                }
            }, {
                "thread_leaves": {
                    "content": "{}:100,1000".format(commented_point),
                    "language": 0,
                    "nicoru": 1,
                    "scores": 1,
                    "thread": str(video_api_info.thread_id),
                    "user_id": video_api_info.user_id,
                    "userkey": video_api_info.user_key,
                    # "waybackkey": wayback_key,
                    # "when": commented_at,
                },
            }
        ]
        thread_key, force_184 = self.get_thread_key(video_api_info.thread_id)
        if thread_key:
            # for official video and the like
            params.append({
                "thread": {
                    "force_184": force_184,
                    "language": 0,
                    "nicoru": 1,
                    "scores": 1,
                    "thread": str(video_api_info.thread_id),
                    "threadkey": thread_key,
                    "user_id": video_api_info.user_id,
                    "version": '20090904',
                    # "waybackkey": wayback_key,
                    # "when": commented_at,
                    "with_global": 1,
                }
            })
            params.append({
                "thread_leaves": {
                    "content": "{}:100,1000".format(commented_point),
                    "force_184": force_184,
                    "language": 0,
                    "nicoru": 1,
                    "scores": 1,
                    "thread": str(video_api_info.thread_id),
                    "threadkey": thread_key,
                    "user_id": video_api_info.user_id,
                    # "waybackkey": wayback_key,
                    # "when": commented_at,
                },
            })
        return {
            "condition": condition,
            "params": params,
        }

    def login(self):
        self.access_to_api("https://secure.nicovideo.jp/secure/login?site=niconico", is_post=True, post_data={
            'mail_tel': Constants.Niconico.LOGIN_ID,
            'password': Constants.Niconico.PASSWORD,
        })

    def access_to_api(self, url, is_post: bool = False, post_data=None, is_json: bool = False):
        response = self.__access_to_api(url, is_post, post_data, is_json)
        logger.debug('url: {}, is_post: {}, post_data: {}, is_json: {}, response: {}, cookies: {}'.format(
            url, is_post, post_data, is_json, response.text, self.http_session.cookies))
        return response

    def __access_to_api(self, url, is_post: bool = False, post_data=None, is_json: bool = False):
        if is_post:
            if is_json:
                return self.http_session.post(url, json=post_data)
            else:
                return self.http_session.post(url, data=post_data)
        else:
            return self.http_session.get(url)

    def get_thread_key(self, thread_id: int) -> Tuple[str, str]:
        result = self.access_to_api("http://flapi.nicovideo.jp/api/getthreadkey?thread={}".format(thread_id))
        result = parse.parse_qs(result.text)
        if result:
            return result['threadkey'][0], result['force_184'][0]
        return "", ""

    def get_post_key(self, block_no, thread) -> str:
        result = self.access_to_api(
            "http://flapi.nicovideo.jp/api/getpostkey?thread={thread}&block_no={block_no}&device=1&version=1&version_sub=6".format(
                thread=thread, block_no=block_no))
        result = parse.parse_qs(result.text)
        return result['postkey'][0]

    def get_wayback_key(self, thread_id: int):
        result = self.access_to_api("http://flapi.nicovideo.jp/api/getwaybackkey?thread={}".format(thread_id))
        result = parse.parse_qs(result.text)
        return result['waybackkey'][0]

    @staticmethod
    def commented_at_string_to_unix_timestamp(d: str) -> int:
        return int(datetime.strptime(d, "%Y/%m/%d").timestamp())

    @staticmethod
    def get_block_no(self, comment_num):
        return int(int(comment_num + 1) / 100)
