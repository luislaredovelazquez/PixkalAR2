from selenium.webdriver.common.by import By


def test_autenticacin(self):
# Test name: Autenticación
# Step # | name | target | value
# 1 | open | https://luislaredov.pythonanywhere.com/ |
    self.driver.get("https://luislaredov.pythonanywhereeeeee.com/")
    # 2 | setWindowSize | 1382x744 |
    self.driver.set_window_size(1382, 744)
    # 3 | click | linkText=Iniciar Sesión |
    self.driver.find_element(By.LINK_TEXT, "Iniciar Sesión").click()
    # 4 | click | id=id_username |
    self.driver.find_element(By.ID, "id_username").click()
    # 5 | type | id=id_username | luislaredov
    self.driver.find_element(By.ID, "id_username").send_keys("luislaredov")
    # 6 | click | id=id_password |
    self.driver.find_element(By.ID, "id_password").click()
    # 7 | type | id=id_password | pixkal1@
    self.driver.find_element(By.ID, "id_password").send_keys("pixkal1@")
    # 8 | click | css=.btn |
    self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

