import unittest
import re
from app import create_app, db
from app.models import User, Movie

'''模擬用戶端測試'''

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies = True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        '''測試index頁面'''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_register_and_login(self):
        '''測試試用者帳號系統'''

        #建立新帳號
        response = self.client.post('/auth/registration', data = {
                    'email' : 'jay@example.com',
                    'username' : 'test',
                    'password' : 'cat',
                    'password2' : 'cat'
                })
        
        self.assertEqual(response.status_code, 302)

        #用新帳號登入
        response = self.client.post('/auth/login', data = {
                    'email' : 'jay@example.com',
                    'password' : 'cat'
                }, follow_redirects = True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search('Hello,\s+test',response.get_data(as_text=True)))
        self.assertTrue('您還沒認證您的帳號' in response.get_data(as_text=True))

        #傳送確認權杖
        user = User.query.filter_by(email = 'jay@example.com').first()
        token = user.gengerate_confirmation_token()
        response = self.client.get('/auth/confirm/{}'.format(token), follow_redirects = True)
        user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('您已經成功認證帳號' in response.get_data(as_text=True))

        #登出
        response = self.client.get('/auth/logout', follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('你已成功登出', response.get_data(as_text= True))

        #登入
        response = self.client.post('/auth/login', data = {
                    'email' : 'jay@example.com',
                    'password' : 'cat'
                }, follow_redirects = True)
        self.assertTrue(re.search('歡迎回來\s+test', response.get_data(as_text=True)))

        #使用者加入電影到電影清單
        test_movie = Movie(title = 'test1')
        test_movie2 = Movie(title = 'test2')
        db.session.add(test_movie)
        db.session.add(test_movie2)
        db.session.commit()
        response = self.client.get('/add_movie/1',follow_redirects = True)
        self.assertTrue('加入成功' in response.get_data(as_text=True))

        #使用者電影清單
        response = self.client.get('/user/movies')
        self.assertTrue('test1' in response.get_data(as_text=True))

        #加入電影清單裡的電影到已觀看清單
        response = self.client.get('/user/add_watched_movie/1', follow_redirects = True)
        self.assertTrue('加入成功' in response.get_data(as_text=True))

        #使用者電影清單
        response = self.client.get('/user/movies')
        self.assertTrue('test1' not in response.get_data(as_text=True))

        #使用者已觀看清單
        response = self.client.get('/user/watched')
        self.assertTrue('test1' in response.get_data(as_text=True))

        #測試使用者重複加入已觀看電影
        response = self.client.get('/add_movie/1', follow_redirects = True)
        self.assertTrue('你已經看過這個電影囉' in response.get_data(as_text=True))

        #測試使用者重覆加入電影清單裡的電影
        response = self.client.get('/add_movie/2', follow_redirects = True)
        response = self.client.get('/add_movie/2', follow_redirects = True)
        self.assertTrue('電影清單裡已經存在該電影', response.get_data(as_text=True))

        #刪除電影清單裡的電影
        response = self.client.get('/user/delete_movie/2',follow_redirects = True)
        self.assertTrue('test2' not in response.get_data(as_text=True))

        #刪除已觀看電影裡的電影
        response = self.client.get('/user/delete_watched_movie/1',follow_redirects = True)
        self.assertTrue('test1' not in response.get_data(as_text=True))

        

        