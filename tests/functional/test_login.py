import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Fixture de Pytest equivalente a @BeforeEach y @AfterEach
@pytest.fixture
def driver():
    # Inicializar el navegador (Chrome en este caso)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Opcional: ejecutar sin interfaz gráfica
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    
    yield driver
    
    # Cerrar el navegador al finalizar la prueba
    driver.quit()

# URL base de la aplicación ejecutándose localmente
BASE_URL = "http://localhost:5000/auth/login"

def test_login_credenciales_validas(driver):
    driver.get(BASE_URL)
    
    # Localizar los campos del formulario[cite: 8]
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "submit")
    
    # Ingresar valores de prueba
    username_input.send_keys("admin")
    password_input.send_keys("password123")
    submit_button.click()
    
    # Resultado esperado: Redirección al index o mensaje de éxito
    WebDriverWait(driver, 5).until(EC.url_changes(BASE_URL))
    assert driver.current_url != BASE_URL

def test_login_contrasena_incorrecta(driver):
    driver.get(BASE_URL)
    
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "submit")
    
    username_input.send_keys("admin")
    password_input.send_keys("error123")
    submit_button.click()
    
    # Resultado esperado: Permanece en login y muestra mensaje de error[cite: 8]
    assert driver.current_url == BASE_URL
    error_message = driver.find_element(By.CSS_SELECTOR, ".alert, .invalid-feedback").text
    assert "Invalid username or password" in error_message or "error" in error_message.lower()

def test_login_campos_vacios(driver):
    driver.get(BASE_URL)
    
    submit_button = driver.find_element(By.ID, "submit")
    submit_button.click()
    
    # Resultado esperado: El formulario valida campos requeridos y no avanza[cite: 8]
    assert driver.current_url == BASE_URL
    username_input = driver.find_element(By.ID, "username")
    # Verifica la validación HTML5 o mensajes de Flask-WTF
    assert username_input.get_attribute("required") or driver.find_elements(By.CSS_SELECTOR, ".invalid-feedback")
