# !/usr/local/bin/python
# -*- coding: utf-8 -*-

from urllib import urlencode

import requests
import json
import re
from BeautifulSoup import BeautifulSoup as BS

zhUrl = lambda x: 'http://www.zhihu.com' + ("/{}".format(x.strip('/')) if x is not None else '')

me = None

class Question:
    """Zhihu question descriptor"""
    
    _session = None
    _re_q = None

    def __init__(self, link, admin=None):
        global me

        if admin is None and me is not None:
            admin = me
        if Question._session is None and admin is not None:
            Question._session = admin.Session

        self.Title = ''
        self.Detail = ''
        self.Topics = set()
        self.ID = ''
        
        if Question._re_q is None:
            Question._re_q = re.compile('(question/([0-9]{8}))')
        
        rl = Question._re_q.search(link)
        try:
            self.Link = zhUrl(rl.group(1))
            self.ID = rl.group(2)
        except:
            raise Exception('Question link error')

    def get_address(self):
        return self.Link

    def to_str(self):
        mystr = [self.Link, self.ID, self.Title]
        for t in self.Topics:
            mystr.append(t.Name)
        return u'\t'.join(mystr)
      
    def get_answer_aid(self):
        if Question._session == None:
            raise Exception('Question not initialized with session')
        pass

    def initial_from_content(self, content):
        pass

class Topic:
    """Zhihu topic descriptor"""

    _session = None

    def __init__(self, link, session, name=None, data_id=None):
        self.Name = name
        self.Link = link
        self.ID = data_id
        self.Questions = set()
        if Topic._session is None:
            Topic._session = session

    def get_address(self):
        return zhUrl('topic/' + str(self.Link))

    def fetch_details(self, s):
        if self.Link == '':
            raise Exception('Link is null. \nit looks like 19556950')
        if s is None:
            return
        url = self.get_address()
        r = s.get(url, headers=Admin.get_post_header(zhUrl('')))
        if r.status_code != 200:
            raise Exception(r.content)
        parser = BS(r.content)
        self.Name = parser.find('div', {'id': 'zh-topic-title'}).h1.string
        self.ID = parser.find('div', {'id': 'zh-topic-desc'})['data-resourceid']

    def get_question_list_page(self):
        return self.get_addr() + '/questions'

    def to_str(self):
        my_str = [self.Link, self.ID, self.Name]
        return u'\t'.join(my_str)


class Answer:
    """ Zhihu User Answer
    """

    def __init__(self, link=None):
        self.ID = link

    def fetch_details(self):
        pass

    def report(self):
        pass

class Admin:
    """ Zhihu User Actions.    """

    UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko)\
                Chrome/27.0.1453.116 Safari/537.36"


    @staticmethod
    def get_post_header(refer):
        _headers = {
            'Origin': zhUrl(None),
            'Referer': refer,
            'User-Agent': Admin.UserAgent,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        return _headers

    def send_request(self, cmd_url, headers, data_):
        data_.append(('_xsrf', self.xsrf))
        page = self.Session.post(cmd_url, headers=headers, data=urlencode(data_))
        return page

    def __init__(self, email=None, password=None):
        self.Email = email
        self.Password = password
        self.Session = requests.Session()
        self.xsrf = ''

    def login(self, email=None, password=None):
        if self.Email is None:
            self.Email = email if email is not None else raw_input('Email: ')
        if self.Password is None:
            self.Password = password if password is not None else raw_input('Password: ')

        page = self.Session.get(zhUrl('#signin'))

        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

        # fetch xsrf.
        self.xsrf = BS(page.content).find('input', {'name': '_xsrf'})['value']

        page = self.send_request(zhUrl('login'),
                                 Admin.get_post_header(zhUrl('')),
                                 [('_xsrf', self.xsrf),
                                  ('email', self.Email),
                                  ('password', self.Password)])

        if page.status_code != 200:
            print 'Login failed.'
            raise Exception('Return code error: {}.'.format(page.status_code))
        print 'User: ' + self.Email + ' has logged in.'

    def get_topic(self, link_id):
        return Topic(link_id, self.Session)

    def remove_topic_from_question(self, topic, question):
        page = self.send_request(zhUrl('topic/unbind'),
                                 Admin.get_post_header(question.get_address()),
                                 [('qid', question.ID),
                                  ('question_id', question.ID),
                                  ('topic_id', topic.ID)])
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

    def append_topic_to_question(self, topic, question):
        page = self.send_request(zhUrl('topic/bind'),
                                 Admin.get_post_header(question.get_address()),
                                 [('qid', question.ID),
                                  ('question_id', question.ID),
                                  ('topic_id', topic.ID),
                                  ('topic_text', topic.Name)])

        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))

    def remove_answer(self, question):
        page = self.Session.get(question.get_address())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))
        
        soup = BS(page.content)
        info = json.loads(soup.find('script', {'data-name': 'my_answer'}).contents[0])
        try:
            if info['is_delete'] == False:
                self.send_request(zhUrl('answer/remove'),
                                  Admin.get_post_header(question.get_address),
                                  [('aid', info['id'])])
        except Exception, e:
            print 'error occured: {}'.format(e)            
            
    def unremove_answer(self, question):
        page = self.Session.get(question.get_address())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))
        
        soup = BS(page.content)
        info = json.loads(soup.find('script', {'data-name': 'my_answer'}).contents[0])
        try:
            if info['is_delete'] == True:
                self.send_request(zhUrl('answer/unremove'),
                                  Admin.get_post_header(question.get_address),
                                  [('aid', info['id'])])
        except Exception, e:
            print 'error occured: {}'.format(e)

    def set_anonymous(self, question):
        page = self.Session.get(question.get_address())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))
        
        soup = BS(page.content)
        info = json.loads(soup.find('script', {'data-name': 'current_question'}).contents[0])
        try:
            self.send_request(zhUrl('question/set_anonymous'),
                              Admin.get_post_header(question.get_address),
                              [('qid', info[0])])
        except Exception, e:
            print 'error occured: {}'.format(e)
        
    def set_public(self, question):
        page = self.Session.get(question.get_address())
        if page.status_code != 200:
            raise Exception('Return code error: {}.'.format(page.status_code))
        
        soup = BS(page.content)
        info = json.loads(soup.find('script', {'data-name': 'current_question'}).contents[0])
        try:
            self.send_request(zhUrl('question/set_public'),
                              Admin.get_post_header(question.get_address),
                              [('qid', info[0])])
        except Exception, e:
            print 'error occured: {}'.format(e)

me = Admin()

if __name__ == '__main__':
    me.login()
    
