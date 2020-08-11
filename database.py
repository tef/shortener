import sys
import sqlite3
import hashlib

from contextlib import contextmanager

import testhelper

def create_url_key(long_url, length=8):
    """
        notes: shake-256 provides variable length digests
        and is immune to extension attacks
    """
    hash = hashlib.shake_256()
    hash.update(long_url.encode('utf8'))
    return hash.hexdigest(length//2)

class Store:
    def __init__(self, filename):
        self.filename = filename
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = sqlite3.connect(self.filename)
            self.create_tables()
        return self._db

    @contextmanager
    def cursor(self):
        c = self.db.cursor()
        try:
            yield c
            self.db.commit()
        except:
            self.db.rollback()
            raise

    def create_tables(self):
        with self.cursor() as c:
            c.execute('''
                create table if not exists short_urls(
                    short_url text primary key,
                    long_url text not null, 
                    timestamp datetime default current_timestamp)
            ''')


    def create_short_url(self, long_url):
        short_url = create_url_key(long_url)
        with self.cursor() as c:
            c.execute(
                '''
                    insert or ignore into short_urls
                    (short_url, long_url) values (?,?)
                ''',
                [short_url, long_url],
            )
        return short_url

    def get_long_url(self, short_url):
        with self.cursor() as c:
            c.execute('select long_url from short_urls where short_url = ?', [short_url])
            row = c.fetchone()
            if row:
                return row[0]

    def delete_short_url(self, short_url):
        with self.cursor() as c:
            c.execute('delete from short_urls where short_url = ?', [short_url])
            return c.rowcount() > 0

    def delete_long_url(self, long_url):
        short_url = create_url_key(long_url)
        with self.cursor() as c:
            c.execute('delete from short_urls where short_url = ?', [short_url])
            return c.rowcount() > 0

class TempStore(Store):
    def __init__(self):
        Store.__init__(self, ":memory:")

TESTS = testhelper.TestRunner()

@TESTS.add()
def test_url_store():
    store = TempStore()
    store.create_tables()

    long_url = "a long url"
    key = create_url_key(long_url)
    short_url = store.create_short_url(long_url)
    assert key == short_url

    out_url = store.get_long_url(short_url)
    assert out_url == long_url

if __name__ == '__main__':
    TESTS.run()
