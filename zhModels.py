# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
import re
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup as BS


zhUrl = lambda x: 'http://www.zhihu.com' + ("/{}".format(x.strip('/')) if x is not None else '')

me = None


class ZhModelException(Exception):
    pass


class ZhServerException(ZhModelException):
    def __init__(self, status_code, msg=''):
        self.status_code = status_code
        self.message = msg


class Question:
    """Zhihu question descriptor"""

    _session = None
    _re_q = None

    def __init__(self, link, title=None, admin=None):
        global me

        if admin is None and me is not None:
            admin = me
        if Question._session is None and admin is not None:
            Question._session = admin.Session

        self.Title = title
        self.Detail = ''
        self.Topics = set()
        self.ID = ''
        self.Link = ''
        self.Token = ''
        self.Answer = None

        if Question._re_q is None:
            Question._re_q = re.compile('(question/([0-9]{8}))')

        rl = Question._re_q.search(link)
        try:
            self.Link = zhUrl(rl.group(1))
            self.Token = rl.group(2)
        except:
            raise Exception('Question link error: %s' % link)

    def get_address(self):
        return self.Link

    def __getattr__(self, name):
        if name == 'AnswerID':
            if Question._session is None:
                raise Exception('Question not initialized with session')
            page = Question._session.get(self.get_address())
            if page.status_code != 200:
                raise Exception('Return code error: {}.'.format(page.status_code))

            soup = BS(page.content)
            info = json.loads(soup.find('script', {'data-name': 'my_answer'}).contents[0])

            try:
                self.AnswerID = info['id']
            except Exception as e:
                print('error occured: {}'.format(e))
            return self.AnswerID

        else:
            return object.__getattr__(name)

    def get_answer_id(self):
        return self.__getattr__('AnswerID')

    def initial_from_content(self, content):
        pass


class Topic:
    """Zhihu topic descriptor"""

    _session = None
    _re_q = None

    def __init__(self, link, name=None, admin=None, data_id=None):
        self.Name = name
        self.ID = data_id
        self.Questions = set()

        if Topic._session is None and admin is not None:
            Topic._session = admin.Session

        if Topic._session is None:
            raise Exception('Class Topic not initialized with admin')

        if Topic._re_q is None:
            Topic._re_q = re.compile('(topic/([0-9]{8}))')

        rl = Topic._re_q.search(link)
        try:
            self.Link = zhUrl(rl.group(1))
            self.Token = str(rl.group(2))
        except:
            raise Exception('Topic link error: %s' % link)

    def get_address(self):
        return zhUrl('topic/' + str(self.Token))

    def fetch_details(self):
        if self.Token == '':
            raise Exception('Link is null. \nit looks like 19556950')
        if Topic._session is None:
            return
        url = self.get_address()
        r = Topic._session.get(url, headers=Admin.post_headers(zhUrl('')))
        if r.status_code != 200:
            raise Exception(r.text)
        parser = BS(r.content)
        self.Name = parser.find('div', {'id': 'zh-topic-title'}).h1.string
        self.ID = parser.find('div', {'id': 'zh-topic-desc'})['data-resourceid']

    def get_question_list_page(self):
        return self.get_addr() + '/questions'

    def to_str(self):
        return '\t'.join([self.Token, self.ID, self.Name])


class Answer:
    """ Zhihu User Answer
    """

    def __init__(self, link=None):
        self.Token = link

    def fetch_details(self):
        pass

    def report(self):
        pass


class Admin:
    """ Zhihu User Actions.    """

    UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"
    # UserAgent = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'

    @staticmethod
    def post_headers(refer):
        _headers = {
            'Origin': zhUrl(None),
            'Referer': refer,
            'User-Agent': Admin.UserAgent,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            # 'Connection': 'Keep-Alive',
        }
        return _headers

    @staticmethod
    def get_headers(refer=None):
        _headers = {
            'Referer': refer,
            'User-Agent': Admin.UserAgent,
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'Keep-Alive',
        }
        return _headers

    def __init__(self, email='', password=''):
        self.Email = email
        self.Password = password

        self.Session = None
        self.xsrf = ''
        self.Hash = ''
        self.Token = ''

    def post(self, cmd_url, data, headers=None, **kwargs):
        if headers is None:
            headers = Admin.post_headers(cmd_url)
        if isinstance(data, dict):
            if '_xsrf' not in data.keys():
                data['_xsrf'] = self.xsrf
        elif isinstance(data, list):
            data.append(('_xsrf', self.xsrf))
        return self.Session.post(cmd_url, data=urlencode(data), headers=headers, **kwargs)

    def get(self, url, headers=None, **kwargs):
        if headers is None:
            headers = Admin.get_headers(url)
        page = self.Session.get(url, headers=headers, **kwargs)
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))
        else:
            return page


    def initialSessionFromCookie(self, chrome_cookie_string):
        cookies_str = str(chrome_cookie_string)
        if self.Session is None:
            self.Session = requests.Session()
        cookies_list = list(cookies_str.split(';'))
        cookies_dict = dict()
        for cookie in cookies_list:
            kv = cookie.split('=')
            # k = kv[0].strip(' ')
            # to simplify cookies, uncomment following 2 lines.
            # if re.match('__utm', k):
            # continue
            cookies_dict[kv[0].strip(' ')] = ('='.join(kv[1:])).strip(' ')

        from requests.cookies import cookiejar_from_dict

        self.Session.cookies = cookiejar_from_dict(cookies_dict)
        self.xsrf = cookies_dict['_xsrf']


    def initialSession(self, session):
        if isinstance(session, requests.Session):
            cookies = dict(session.cookies)
            if '_xsrf' in cookies.keys():
                self.xsrf = cookies['_xsrf']
                self.Session = session


    def login(self, email=None, password=None):
        if self.Email is None:
            self.Email = email if email is not None else input('Email: ')
        if self.Password is None:
            self.Password = password if password is not None else input('Password: ')
        if self.Session is None:
            self.Session = requests.Session()

        page = self.Session.get(zhUrl('#signin'), headers=Admin.get_headers())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

        # fetch xsrf.ee
        self.xsrf = BS(page.text).find('input', {'name': '_xsrf'})['value']
        # self.Session.cookies.update(page.cookies)
        data_ = [('_xsrf', self.xsrf),
                 ('email', self.Email),
                 ('password', self.Password),
                 ('rememberme', 'y')]

        page = self.Session.post(zhUrl('login'),
                                 headers=Admin.post_headers(zhUrl('/')),
                                 data=urlencode(data_))

        if page.status_code != 200:
            print('Login failed. Return code: %s' % page.status_code)

        if BS(page.text).find('form', class_='login') is not None:
            print('Login failed, please verify captcha.')
        else:
            print('User: ' + self.Email + ' has logged in.')

    def getTopic(self, link_id):
        return Topic(link_id, self.Session)

    def removeTopicFromQuestion(self, topic, question):
        page = self.post(zhUrl('topic/unbind'),
                         [('qid', question.ID),
                          ('question_id', question.ID),
                          ('topic_id', topic.ID)],
                         Admin.post_headers(question.get_address()))
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

    def appendTopicToQuestion(self, topic, question):
        page = self.post(zhUrl('topic/bind'),
                         [('qid', question.ID),
                          ('question_id', question.ID),
                          ('topic_id', topic.ID),
                          ('topic_text', topic.Name)],
                         Admin.post_headers(question.get_address()))

        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

    def removeAnswer(self, question):
        self.post(zhUrl('answer/remove'), [('aid', question.get_answer_id())],
                  Admin.post_headers(question.get_address()))

    def unremoveAnswer(self, question):
        self.post(zhUrl('answer/unremove'), [('aid', question.get_answer_id())],
                  Admin.post_headers(question.get_address()))

    def setAnonymous(self, question):
        page = self.Session.get(question.get_address())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

        soup = BS(page.content)
        info = json.loads(soup.find('script', {'data-name': 'current_question'}).contents[0])
        try:
            self.post(zhUrl('question/set_anonymous'), [('qid', info[0])], Admin.post_headers(question.get_address))
        except Exception as e:
            print('error occured: {}'.format(e))

    def setPublic(self, question):
        page = self.Session.get(question.get_address())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

        soup = BS(page.content)
        info = json.loads(soup.find('script', {'data-name': 'current_question'}).contents[0])
        try:
            self.post(zhUrl('question/set_public'), [('qid', info[0])], Admin.post_headers(question.get_address))
        except Exception as e:
            print('error occured: {}'.format(e))


    def fetchMemberSoup(self, people_token):
        followees = zhUrl('people/' + people_token.strip('/ ') + '/followees')
        page = self.get(followees)
        return BS(page.content)

    @staticmethod
    def findMemberHashIdFromSoup(people_soup):
        if not isinstance(people_soup, BS):
            raise ZhModelException('Parameter "people_soup" should be an instance of BeautifulSoup')
        soup = people_soup
        c_p = soup.find('script', {'data-name': 'current_people'})
        c_p_l = list(json.loads(c_p.text))
        if len(c_p_l) == 0:
            raise ZhModelException('Unexpected people info')
        return c_p_l[-1]

    def fetchMemberHashId(self, people_token):
        return self.findMemberHashIdFromSoup(self.fetchMemberSoup(people_token))

    def memberFollowBase(self, hash_id, command):
        COMMAND_URL = 'http://www.zhihu.com/node/MemberFollowBaseV2'
        command = str(command).lower()
        if command not in ['follow_member', 'unfollow_member']:
            raise ZhModelException('Unknown follow command.')

        data = {'method': command, 'params': json.dumps({"hash_id": hash_id}), '_xsrf': self.xsrf}
        self.post(COMMAND_URL, data=data)

    def followByHashId(self, people_hash_id):
        self.memberFollowBase(people_hash_id, 'follow_member')

    def unfollowByHashId(self, people_hash_id):
        self.memberFollowBase(people_hash_id, 'unfollow_member')

    def follow(self, people_token):
        self.followByHashId(self.fetchMemberHashId(people_token))

    def unfollow(self, people_token):
        self.unfollowByHashId(self.fetchMemberHashId(people_token))

    def followColumn(self, column_id):
        COMMAND_URL = 'http://www.zhihu.com/node/ColumnFollowBaseV2'
        data = {'method': 'follow_column', 'params': json.dumps({'column_id': str(column_id)})}
        self.post(COMMAND_URL, data)

    def checkLogin(self):
        page = self.get(zhUrl(''))
        soup = BS(page.content)
        __me = soup.find('script', {'data-name': 'current_user'})
        print(__me.text)

    def clone(self, another_token):
        another_soup = self.fetchMemberSoup(another_token)
        another_hash = self.findMemberHashIdFromSoup(another_soup)

        current_col_num = 0
        COLUMN_LIST_URL = 'http://www.zhihu.com/node/ProfileFollowedColumnsListV2'
        while True:
            params = {"offset": current_col_num, "limit": 20, "hash_id": another_hash}
            page = self.post(COLUMN_LIST_URL, data={'method': 'next', 'params': json.dumps(params)})
            if page.status_code != 200:
                break
            resp = json.loads(page.text)
            if resp['r'] == 0:
                if len(resp['msg']) != 0:
                    for column in resp['msg']:
                        soup = BS(column)
                        # button data-follow="c:button"
                        c_id_str = str(soup.find('button', {'data-follow': 'c:button'})['id'])
                        c_id = c_id_str.split('-')[-1]
                        self.followColumn(c_id)

                else:
                    break
            current_col_num += len(resp['msg'])

        proceeded_num = 0
        FOLLOWEE_LIST_URL = 'http://www.zhihu.com/node/ProfileFolloweesListV2'
        while True:
            params = {'offset': proceeded_num, "order_by": "created", "hash_id": another_hash}
            page = self.post(FOLLOWEE_LIST_URL, data=[('method', 'next'), ('params', json.dumps(params))])
            if page.status_code != 200:
                break
            resp = json.loads(page.text)
            if resp['r'] == 0:
                if len(resp['msg']) != 0:
                    for people in resp['msg']:
                        soup = BS(people)
                        hash_ = soup.find('button', {'data-follow': 'm:button'})['data-id']
                        self.followByHashId(hash_)
                else:
                    break
            proceeded_num += len(resp['msg'])


if __name__ == '__main__':
    me = Admin()
    me.login()
    
