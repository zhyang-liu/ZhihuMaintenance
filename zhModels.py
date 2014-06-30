# !/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
import re
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup as BS


zhUrl = lambda x: 'http://www.zhihu.com' + ("/{}".format(x.strip('/')) if x is not None else '')

me = None


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


    def post(self, cmd_url, data_, headers=None):
        if headers is None:
            headers = Admin.post_headers(zhUrl('/'))
        data_.append(('_xsrf', self.xsrf))
        return self.Session.post(cmd_url, headers=headers, data=urlencode(data_))

    def __init__(self, email=None, password=None):
        self.Email = email
        self.Password = password
        self.Session = requests.Session()
        self.xsrf = ''

    def login(self, email=None, password=None):
        if self.Email is None:
            self.Email = email if email is not None else input('Email: ')
        if self.Password is None:
            self.Password = password if password is not None else input('Password: ')

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
            print('Login failed.')
            raise Exception('Return code error: {}.'.format(page.status_code))
        print('User: ' + self.Email + ' has logged in.')

    def get_topic(self, link_id):
        return Topic(link_id, self.Session)

    def remove_topic_from_question(self, topic, question):
        page = self.post(zhUrl('topic/unbind'),
                         [('qid', question.ID),
                          ('question_id', question.ID),
                          ('topic_id', topic.ID)],
                         Admin.post_headers(question.get_address()))
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

    def append_topic_to_question(self, topic, question):
        page = self.post(zhUrl('topic/bind'),
                         [('qid', question.ID),
                          ('question_id', question.ID),
                          ('topic_id', topic.ID),
                          ('topic_text', topic.Name)],
                         Admin.post_headers(question.get_address()))

        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

    def remove_answer(self, question):
        self.post(zhUrl('answer/remove'), [('aid', question.get_answer_id())],
                  Admin.post_headers(question.get_address()))

    def unremove_answer(self, question):
        self.post(zhUrl('answer/unremove'), [('aid', question.get_answer_id())],
                  Admin.post_headers(question.get_address()))

    def set_anonymous(self, question):
        page = self.Session.get(question.get_address())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

        soup = BS(page.content)
        info = json.loads(soup.find('script', {'data-name': 'current_question'}).contents[0])
        try:
            self.post(zhUrl('question/set_anonymous'), [('qid', info[0])], Admin.post_headers(question.get_address))
        except Exception as e:
            print('error occured: {}'.format(e))

    def set_public(self, question):
        page = self.Session.get(question.get_address())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

        soup = BS(page.content)
        info = json.loads(soup.find('script', {'data-name': 'current_question'}).contents[0])
        try:
            self.post(zhUrl('question/set_public'), [('qid', info[0])], Admin.post_headers(question.get_address))
        except Exception as e:
            print('error occured: {}'.format(e))


if __name__ == '__main__':
    me = Admin()
    me.login()
    
