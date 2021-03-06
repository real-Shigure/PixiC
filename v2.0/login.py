# coding=utf8
from selenium import webdriver
from requests.cookies import RequestsCookieJar
import json
import re
import requests

from config import COOKIE_NAME, COOKIE_UPDATE_ENABLED, PRO_DIR, USER_ID
from logstr import log_str

class Login(object):

	def __init__(self):
		"""
		初始化操作
		flag用于判断是否需要请求以获得uid
		cookie用于存储selenium获取的cookie
		"""
		self.host_url = "https://www.pixiv.net/"
		self.user_id = ""
		self.flag = True if USER_ID == "" else False
		self.cookie = RequestsCookieJar()
		
	def check(self):
		"""
		获取cookie
		"""
		self.get_cookie() if COOKIE_UPDATE_ENABLED == True else self.set_cookie()
		if self.cookie == []:
			log_str("请使用Chrome登录Pixiv,以便获取cookie")
			log_str("请打开代理软件")
			exit()
		log_str("{} 初始化完成！".format(__file__.split("\\")[-1].split(".")[0]))

	def get_cookie(self):
		'''
		配置selenium以访问站点,持久化cookie
		'''
		chrome_options = webdriver.ChromeOptions()
		# 静默模式可能会导致获取不了cookie
		# chrome_options.add_argument('--headless')	
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--start-maximized')
		# 取消警告语
		chrome_options.add_experimental_option('useAutomationExtension', False)
		chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
		# 用户目录配置
		chrome_options.add_argument('user-data-dir='+PRO_DIR)
		driver = webdriver.Chrome(chrome_options=chrome_options)
		driver.get(self.host_url)
		cookies = driver.get_cookies()
		driver.quit()

		with open(COOKIE_NAME, "w") as fp:
		    json.dump(cookies, fp)

		self.set_cookie()

	def set_cookie(self):
		'''
		读取并返回cookie
		'''
		jar = RequestsCookieJar()
		with open(COOKIE_NAME, "r", encoding="utf8") as fp:
			# readlines(),读取之后,文件指针会在文件末尾,再执行只会读到空[]
			if fp.readlines() == []:
				log_str("cookie为空,请设置'COOKIE_UPDATE_ENABLED'以更新cookie")
				exit()
			fp.seek(0)
			cookies = json.load(fp)
			for cookie in cookies:
				self.cookie.set(cookie['name'], cookie['value'])
				jar.set(cookie['name'], cookie['value'])
		
		# 获取user_id
		if self.flag == True:
			self.user_id = self.get_user_id()
		else:
			self.user_id = USER_ID
		return jar
		
	def get_user_id(self):
		user_id = re.findall(r'''.*?,user_id:"(.*?)",.*?''',requests.get(self.host_url,cookies=self.cookie).text.replace(" ",""))[0]
		return user_id

client = Login()
# if __name__ == '__main__':
# 	a = Login().cookie
# 	print(a)
	# Login()