from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
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
