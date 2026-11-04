from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def iniciar_sesion(driver):
    driver.get("http://127.0.0.1:5000/auth/login")

    url_login = driver.current_url

    driver.find_element(By.ID, "username").send_keys("selenium_test")
    driver.find_element(By.ID, "password").send_keys("test1234")
    driver.find_element(By.ID, "submit").click()

    WebDriverWait(driver, 10).until(
        EC.url_changes(url_login)
    )


def test_editar_perfil_correctamente(driver):
    iniciar_sesion(driver)
    driver.get("http://127.0.0.1:5000/edit_profile")

    about_me = driver.find_element(By.ID, "about_me")
    about_me.clear()
    about_me.send_keys("Estudiante de Ciencias de la Computacion")

    driver.find_element(By.ID, "submit").click()

    mensaje = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "alert"))
    )

    assert "Your changes have been saved." in mensaje.text
    assert driver.find_element(By.ID, "about_me").get_attribute("value") == \
        "Estudiante de Ciencias de la Computacion"


def test_editar_perfil_username_vacio(driver):
    iniciar_sesion(driver)
    driver.get("http://127.0.0.1:5000/edit_profile")

    username = driver.find_element(By.ID, "username")
    username.clear()

    # Enviamos el formulario para comprobar la validación del servidor.
    driver.execute_script(
        "HTMLFormElement.prototype.submit.call(arguments[0].form);",
        username
    )

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "invalid-feedback"))
    )

    assert "Este campo es obligatorio." in error.text


def test_editar_perfil_about_me_muy_largo(driver):
    iniciar_sesion(driver)
    driver.get("http://127.0.0.1:5000/edit_profile")

    about_me = driver.find_element(By.ID, "about_me")
    texto_largo = "A" * 141

    driver.execute_script(
        """
        arguments[0].value = arguments[1];
        HTMLFormElement.prototype.submit.call(arguments[0].form);
        """,
        about_me,
        texto_largo
    )

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "invalid-feedback"))
    )

    assert "El campo debe tener entre 0 y 140 caracteres." in error.text
