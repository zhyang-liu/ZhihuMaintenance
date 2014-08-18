ZhihuMaintenance
================
#class Admin
## 登陆
在做大部分操作前，需要有一个已经登录的 session。通过以下几个函数可以用不同方法创建 session。

1. 使用 cookie 创建 session

    `initialSessionFromCookie(chrome_cookie_string)`
    
    通过已经登录的 Chrome 的 cookies 来初始化 session，cookie 字符串即开发者工具的 network 
    检测到的 cookie字符串，完整复制即可。
    
    使用这种方法获得的 Admin 对象，只有 xsrf 被初始化，其他成员变量均为空字符串或 None。

2. 从已有 session 恢复

    `initialSession(session)`
    
    如果已经使用某些方法（如 pickle）将 session保存到文件，那么可以直接使用这个方法来初始化
    session。
    
    使用这种方法获得的 Admin 对象，只有 xsrf 被初始化，其他成员变量均为空字符串或 None。
    
3. 传统的登陆方法

    `login(email, password)`
 
    使用 Email 与 Password 配合的传统方式登陆知乎。但是由于验证码的存在，这个方法经常失效。
    
## GET and POST
* GET 
    
    `get(url, headers=None, **kwargs)`

    requests 库的 GET 方法被再次封装。在默认情况下，使用符合知乎要求的 headers 代替 requests 默认的 headers。
    具体用法参见 requests.get()。
    
* POST

    `post(url, data, headers=None, **kwargs)`

    requests 库的 POST 方法被再次封装。在默认情况下，使用符合知乎要求的 headers 代替 requests 默认的 headers。
    具体用法参见 requests.post()。

## 话题操作
* 获取话题

    `getTopic(link)`

    该方法返回一个 `Topic` 对象。该对象的 `Link` 和 `Token` 已被填写。其余信息请参见 `class Topic` 章节。

* 向问题添加话题、移除话题

    ```python
    appendTopicToQuestion(topic, question)
    removeTopicFromQuestion(topic, question)
    ```
    
    该方法需要已经获取 Topic 和 Question 的 ID（**此 ID 并非 URL 中的 8 位数字**），详见相关章节。
    

## 回答操作
* 删除回答 / 撤销删除回答

    ```python 
    removeAnswer(question)
    unremoveAnswer(question)
    ```
    
    该方法需要已经获取 Question 的 URL-Token（** 即 URL 中的 8 位数字**）。
    
* 使用匿名身份 / 撤销使用匿名身份

    ```python
    setAnonymous(question)
    setPublic(question)
    ```
    
    该方法需要已经获取 Question 的 URL-Token（** 即 URL 中的 8 位数字**）。


## 用户操作
* 关注 / 取消关注用户

    ```python
    follow(people_token)
    unfollow(people_token)
    ```

    `people_token` 即用户网址中，`/people/` 后边的那一部分内容。
    
* 克隆目标用户关注对象（含专栏和用户）

    `clone(people_token)`
    
    关注目标用户关注的所有用户和专栏，`people_token` 即用户网址中 `/people/` 后边的那一部分内容。
    
## 专栏操作
* 关注专栏 

    `followColumnById(column_id)`
    
    **TODO: 待做成根据专栏 URL / token 关注的函数**
    
    关注指定 ID 的专栏，专栏可在专栏的「关注」按钮中找到。
    
==========================    
#** TODO: 以下内容、接口待整理和更新**
==========================
#class Question
## \_\_init\_\_(self, link, title=None, admin=None)

该初始化方法为 Question 对象提供 Link 和 Token（URL-Token），其他成员不会被初始化。在初次构建 Question 的时候应当传入一个 Admin 实例，该 Admin 实例会被保存在 Question 的全局成员（static member）\_session 中。
    
## get\_answer\_id()

该方法获取当前 Question.\_session 对应的用户的 answer\_id 。
    
## get_address()

获取当前问题的 URL 地址。

#class Topic
##\_\_init\_\_(self, link, name=None, admin=None, data_id=None)

与 Question 类似，初次构造时应传入一个 Admin 实例。

##fetch\_details()

获取 Topic 的名称和 ID（**不同于 URL-Token 的 8 位数字**）

##get\_question\_list\_page()

获取该话题的「所有问题」的 URL。

#class Answer
## *尚未完成*

