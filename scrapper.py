from csv import DictWriter
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains

"""
Global Variables
"""

output_csv_path = 'out.csv'
delimiter = ';'
url = "https://www.dges.gov.pt/coloc/2023/col1listas.asp"

def get_data_select():
  """
  Retrieve the select element containing all courses offered by the University of Aveiro.
  """

  data_select_element = driver.find_element(by=By.XPATH, value='/html/body/div/table/tbody/tr/td/div[2]/form/table[2]/tbody/tr/td/select')
  data_select = Select(data_select_element)

  return data_select

def get_table_lines():
  """
  Get the table lines
  """

  table_xpath = '/html/body/div/table/tbody/tr/td/div[2]/table[3]/tbody'
  table = driver.find_element(by=By.XPATH, value=table_xpath)

  return table.find_elements(by=By.CSS_SELECTOR, value="tr")

def get_line_content(line):
  """
  Get id and value from line
  """

  return list(map(
    lambda cell: cell.text.strip().replace('\n', ' '), 
    line.find_elements(by=By.XPATH, value='td')
  ))

def get_header():
  """
  Get table header from datatable
  """

  header_xpath = '/html/body/div/table/tbody/tr/td/div[2]/table[2]/tbody/tr'
  header = driver.find_element(by=By.XPATH, value=header_xpath)

  return get_line_content(header)

def goTo(xpath: str):
  """
  Click on element, and go to and given path
  """

  btn = driver.find_element(by=By.XPATH, value=xpath)
  ActionChains(driver).click(btn).perform()

"""
Setup web driver, in this case it was used msedge web driver to the web scaper
"""

service = webdriver.EdgeService(executable_path='driver\\msedgedriver.exe')
options = webdriver.EdgeOptions()
options.add_argument("--enable-chrome-browser-cloud-management")
options.add_argument('--remote-debugging-pipe')
options.add_experimental_option("detach", True)

driver = webdriver.Edge(service=service, options=options)
driver.get(url)

"""
Choose to scrap universities students
"""

goTo('/html/body/div/table/tbody/tr/td/div[2]/table[2]/tbody/tr[1]/td/ul/li/a')

"""
Select University Aveiro
"""

university_select_element = driver.find_element(by=By.XPATH, value='/html/body/div/table/tbody/tr/td/div[2]/form/table[2]/tbody/tr/td/select')
university_select = Select(university_select_element)
university_select.select_by_value('0300')

"""
Go to "Lista de Colocados"
"""

goTo('/html/body/div/table/tbody/tr/td/div[2]/form/table[2]/tbody/tr[2]/td/input[4]')

"""
Request Courses list
"""

data_select = get_data_select()

if len(data_select.options) == 0:
  driver.close()

  print("There is no element to scrap on")
  exit()

"""
Get All Options from the course select element
"""

option_values = list(map(
  lambda option: option.get_property('value'),
  data_select.options
))

header = []
csvLines = []

"""
For each option, inspect students and grab their information and append it to the csvLines array to be later converted to csv
"""

for option in option_values:
  data_select = get_data_select()
  data_select.select_by_value(option)

  goTo('/html/body/div/table/tbody/tr/td/div[2]/form/table[2]/tbody/tr[2]/td/input[3]')

  if option == option_values[0]:
    header = get_header()

  lines = get_table_lines()

  for line in lines:
    csvLine = get_line_content(line)
    csvLines.append({ header[0]: csvLine[0], header[1]: csvLine[1] })

  driver.back()

driver.close()

"""
After ghather all rows information about the students, store it on a csv file.
"""

print(f"Storing csv... on {output_csv_path}")
with open(output_csv_path, "w", encoding="UTF-8", newline="") as csv_file:
    writer = DictWriter(csv_file, fieldnames=header, delimiter=delimiter)
    writer.writeheader()

    for line in csvLines:
      writer.writerow(line)

csv_file.close()