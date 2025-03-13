from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Selenium 설정
driver = webdriver.Chrome()  # 크롬 드라이버 경로를 지정해야 할 수 있습니다.
driver.get("https://tossinvest.com/stocks/A005930/community")

try:
    # 페이지가 완전히 로드될 때까지 기다립니다.
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    print("Page loaded successfully.")

    # 최신순 버튼 클릭
    try:
        # 정확한 XPath를 사용하여 요소가 나타날 때까지 기다립니다.
        latest_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="stock-content"]/div/div/section/section/section/button'))
        )
        latest_button.click()
        print("Latest button clicked.")
        time.sleep(2)  # 페이지가 갱신될 시간을 기다립니다.
    except Exception as e:
        print("Error clicking latest button:", e)

    # 스크롤을 통해 더 많은 댓글 로드
    scroll_limit = 10  # 스크롤을 수행할 최대 횟수
    scroll_count = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    while scroll_count < scroll_limit:
        # 스크롤을 끝까지 내립니다.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 새로운 콘텐츠가 로드될 시간을 기다립니다.

        # 새로운 높이를 계산하고, 이전 높이와 비교합니다.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 더 이상 새로운 콘텐츠가 없으면 종료
        last_height = new_height
        scroll_count += 1

    # 페이지 소스를 가져옵니다.
    page_source = driver.page_source
    print("Page source retrieved.")

    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(page_source, 'html.parser')

    # 댓글 요소를 찾습니다.
    comments = soup.select('div._1p19xcx1')

    # 댓글 텍스트와 시간을 추출합니다.
    comment_list = []
    for comment in comments:
        try:
            # 텍스트와 시간을 추출
            text_element = comment.select_one('span.tw-1r5dc8g0._60z0ev1._60z0ev6._60z0ev0._1tvp9v41._1sihfl60')
            text = text_element.get_text(strip=True) if text_element else "No text"
            time_info_element = comment.select_one('span.tw-1r5dc8g0')
            time_info = time_info_element.get_text(strip=True) if time_info_element else "No time"
            comment_list.append({'Text': text, 'Time': time_info})
        except AttributeError as e:
            print("Error extracting comment data:", e)

    # 판다스를 사용하여 데이터프레임으로 변환
    df = pd.DataFrame(comment_list)

    # 데이터프레임을 CSV 파일로 저장
    df.to_csv('comments.csv', index=False, encoding='utf-8-sig')
    print("Comments saved to CSV.")

except Exception as e:
    print("An error occurred:", e)

finally:
    # 드라이버를 종료합니다.
    driver.quit()
    print("Browser closed.")
