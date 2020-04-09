import json
import time
from django.test import TestCase, Client
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from users.models import User

# Create your tests here.

class TestUsersViews(TestCase):
    
    def setUp(self):
        print("Starting tests")
        self.client = Client()
        self.user = User.objects.create(username="test_user")
        self.user.set_password("12345")
        self.user.save()
        
        self.user_first = User.objects.create(username="test_user_first")
        self.user_first.set_password("12345")
        self.user_first.save()
        
        self.logged_in = self.client.login(username="test_user", password="12345")
        
    def test_profile_details(self):
        response = self.client.get('/users/profile/')
        content = json.loads(response.content)
        self.assertTrue(response.status_code == 200)
        self.assertEqual(content['profile']['username'], 'test_user')
        
    def test_contacts_list(self):
        response = self.client.get('/users/list')
        self.assertLessEqual(response.status_code, 200)
        self.assertJSONNotEqual(response.content, '{"users": []}')
        
        
    def test_search_users(self):
        response = self.client.get('/users/search_users?name=test&limit=5')
        self.assertFalse(response.status_code == 404)
        self.assertJSONEqual(response.content, '{"users": [{"id": 1, "username": "test_user", "first_name": "", "avatar": ""}, {"id": 2, "username": "test_user_first", "first_name": "", "avatar": ""}]}')
        
        
    def tearDown(self):
        print("Tests ended")


class SelenuimTest(TestCase):
    
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()
        self.driver.get("https://localhost:8080/")
        #time.sleep(0.5)
        
    def test_login_success(self):
        try:
            elem = self.driver.find_element_by_class_name('btn-vk')
            elem.click()
        except Exception as ex:
            print(str(ex).strip())
            print("Element not found")
        finally:
            self.driver.close()
        
    def test_login_failure(self):
        try:
            elem = self.driver.find_element_by_class_name('btn-vk2')
            elem.click()
            self.driver.close()
        except Exception as ex:
            print(str(ex).strip())
            print("Element not found")
        finally:
            self.driver.close()