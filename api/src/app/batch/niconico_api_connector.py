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


class VideoDataGetError(Exception):
    pass


class CommentDataGetError(Exception):
    pass


class NiconicoAPIConnector:
    def __init__(self):
        self.http_session = requests.Session()  # this session has cookie
        self.__login()  # login for following api access

    def get_video_api_info(self, video_id: str):
        result = self.__access_to_api("http://flapi.nicovideo.jp/api/getflv/" + video_id)
        result = parse.parse_qs(result.text)
        if not result or 'thread_id' not in result:
            raise VideoDataGetError('failed to get video api info from niconico API. video_id -> {}, response -> {}'.format(video_id, result))
        return VideoAPIInfo(video_id, int(result['thread_id'][0]), result['user_id'][0], result['ms'][0],
                            result['userkey'][0])

    def get_comments(self, video_id: str) -> Comments:
        try:
            video_api_info = self.get_video_api_info(video_id)
            params_and_condition = self.__get_params_for_comment(video_api_info)
            result = self.__access_to_api(video_api_info.comment_server_url_json, is_post=True,
                                          post_data=params_and_condition, is_json=True)
            data = result.json()
            assert data
            return Comments(data)
        except VideoDataGetError:
            raise
        except:
            raise CommentDataGetError

    def get_video_info(self, video_id: str) -> VideoInfo:
        api_response = self.__access_to_api("http://ext.nicovideo.jp/api/getthumbinfo/" + video_id)
        root = ElementTree.fromstring(api_response.content)
        data = {child.tag: child.text for child in root[0]}
        if not data or 'video_id' not in data:
            raise VideoDataGetError('failed to get video info from niconico API. video_id -> {}, response -> {}'.format(video_id, data))
        return VideoInfo(data)

    def __get_params_for_comment(self, video_api_info: VideoAPIInfo):
        """make parameters to get comment

        :param video_api_info: VideoAPIInfo
        :return: parameter dict
        """
        video_info = self.get_video_info(video_api_info.video_id)
        commented_point = Util.get_commented_point(video_info.length)
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
                    "with_global": 1,
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
                },
            }
        ]
        thread_key, force_184 = self.__get_thread_key(video_api_info.thread_id)
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
                },
            })
        return params

    def __login(self):
        """login to niconico with specified account. login status will be saved on cookie."""
        self.__access_to_api("https://secure.nicovideo.jp/secure/login?site=niconico", is_post=True, post_data={
            'mail_tel': Constants.Niconico.LOGIN_ID,
            'password': Constants.Niconico.PASSWORD,
        })

    def __get_thread_key(self, thread_id: int) -> Tuple[str, str]:
        """get video thread key to get official video comments.

        :param thread_id: video thread id
        :return: Tuple of threadkey and force_184
        """
        result = self.__access_to_api("http://flapi.nicovideo.jp/api/getthreadkey?thread={}".format(thread_id))
        result = parse.parse_qs(result.text)
        if result:
            return result['threadkey'][0], result['force_184'][0]
        return "", ""

    def __access_to_api(self, url, is_post: bool = False, post_data=None, is_json: bool = False):
        response = self.__access_to_api_impl(url, is_post, post_data, is_json)
        logger.debug('url: {}, is_post: {}, post_data: {}, is_json: {}, cookies: {}'.format(
            url, is_post, post_data, is_json, self.http_session.cookies))
        return response

    def __access_to_api_impl(self, url, is_post: bool = False, post_data=None, is_json: bool = False):
        if is_post:
            if is_json:
                return self.http_session.post(url, json=post_data)
            else:
                return self.http_session.post(url, data=post_data)
        else:
            return self.http_session.get(url)
