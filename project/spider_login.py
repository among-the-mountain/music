from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# 配置Chrome选项（支持无头模式）
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("http://127.0.0.1:5000/")

# 输入账号密码
driver.find_element(By.NAME, "user").send_keys("admin")
driver.find_element(By.NAME, "pwd").send_keys("123456")

# 点击登录
driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

time.sleep(1)

# 获取表格数据
trs = driver.find_elements(By.TAG_NAME, "tr")
for tr in trs:
    print(tr.text)

driver.quit()
