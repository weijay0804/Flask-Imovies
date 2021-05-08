import unittest
from app import create_app, db
from app.models import User
import time

'''使用者系統測試'''

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_password_setter(self):
        '''測試使用者密碼不為空'''
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        '''測試使用者密碼屬性為不可讀取'''
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        '''測試使用者密碼是否不相等'''
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        '''測試雜湊值的salt為隨機'''
        u = User(password = 'cat')
        u2 = User(password = 'cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        '''測試有效值的使用者權杖'''
        u = User(password = 'cat')
        db.session.add(u)
        db.session.commit()
        token = u.gengerate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        '''測試無效值的使用者權杖'''
        u1 = User(password = 'cat')
        u2 = User(password = 'dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.gengerate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        '''測試權杖到期時間'''
        u = User(password = 'cat')
        db.session.add(u)
        db.session.commit()
        token = u.gengerate_confirmation_token(expiration=1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_password_token(self):
        '''測試有效的更改密碼token'''
        u = User(password = 'cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_passsword_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_password_token(self):
        '''測試無效的更改密碼token'''
        u = User(password = 'cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_passsword_token()
        self.assertFalse(u.reset_password(token + 'a', 'dog'))
        self.assertTrue(u.verify_password('cat'))

    def test_valid_change_email_token(self):
        '''測試有效的更改email token'''
        u = User(email = 'a@example.com', password = 'cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_change_email_token('b@example.com')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'b@example.com')

    def test_invalid_change_email_token(self):
        '''測試無效的更改email token'''
        u1 = User(email = 'a@example.com', password = 'cat')
        u2 = User(email = 'b@example.com', password = 'dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_change_email_token('c@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'b@example.com')
    
    def test_duplicate_change_email_token(self):
        u1 = User(email = 'a@example.com', password = 'cat')
        u2 = User(email = 'b@example.com', password = 'dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_change_email_token('a@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'b@example.com')