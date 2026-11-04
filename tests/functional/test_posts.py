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


def test_crear_publicacion_correctamente(driver):
    iniciar_sesion(driver)
    driver.get("http://127.0.0.1:5000/")

    texto = "Publicacion de prueba Selenium"

    driver.find_element(By.ID, "post").send_keys(texto)
    driver.find_element(By.ID, "submit").click()

    mensaje = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "alert"))
    )

    assert "Your post is now live!" in mensaje.text

    publicacion = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            f"//span[starts-with(@id, 'post') and text()='{texto}']"
        ))
    )

    assert publicacion.text == texto


def test_crear_publicacion_vacia(driver):
    iniciar_sesion(driver)
    driver.get("http://127.0.0.1:5000/")

    post = driver.find_element(By.ID, "post")

    driver.execute_script(
        "HTMLFormElement.prototype.submit.call(arguments[0].form);",
        post
    )

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "invalid-feedback"))
    )

    assert "Este campo es obligatorio." in error.text


def test_crear_publicacion_mayor_a_140_caracteres(driver):
    iniciar_sesion(driver)
    driver.get("http://127.0.0.1:5000/")

    post = driver.find_element(By.ID, "post")
    texto_largo = "A" * 141

    driver.execute_script(
        """
        arguments[0].value = arguments[1];
        HTMLFormElement.prototype.submit.call(arguments[0].form);
        """,
        post,
        texto_largo
    )

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "invalid-feedback"))
    )

    assert "El campo debe tener entre 1 y 140 caracteres." in error.text
