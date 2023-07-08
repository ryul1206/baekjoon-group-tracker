from typing import List, Dict
import os
import time
import yaml
import random
import argparse
import requests
from bs4 import BeautifulSoup
from report import Logger


def get_html(problem_id, user_id):
    url = f"https://www.acmicpc.net/status?problem_id={problem_id}&user_id={user_id}&language_id=-1&result_id=-1"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/89.0.4389.82 Safari/537.36",
    }

    response = requests.get(url, headers=headers)
    return response.text


def crawl_table(html) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "table table-striped table-bordered"})

    # 테이블 헤더 추출
    headers = [header.text for header in table.find_all("th")]

    # 테이블 내용 추출
    rows = table.find_all("tr")
    results = []
    for row in rows:
        result = process_row(row, headers)
        if result:
            results.append(result)
    return results


def process_row(row, headers) -> Dict:
    data = row.find_all("td")
    result = {}
    if data:
        for index in range(len(headers)):
            if headers[index] == "언어":

                # 첫번째 a 태그의 텍스트와 하이퍼링크 추출 <- 이걸 보려면 Selenium으로 로그인해야 함
                # <a href="https://www.acmicpc.net/source/63132879">Python 3</a>
                # => "Python 3", "https://www.acmicpc.net/source/63132879"
                # result["언어"] = data[index].find("a").text
                # result["코드"] = data[index].find("a")["href"]
                # 로그인 없이는 링크를 얻을 수 없고, 다음의 결과가 주어짐
                # <td>Python 3</td>
                result["언어"] = data[index].text.strip()

            elif headers[index] == "제출한 시간":
                # a 태그에서 data-timestamp 속성 추출 (data-original-title이나 title 속성은 비어있는 경우가 있음)
                # data-timestamp="1688751647"
                # => "2023년 7월 8일 02:40:47"
                epoch = data[index].find("a")["data-timestamp"]
                result["제출한 시간"] = time.strftime("%Y년 %m월 %d일 %H:%M:%S", time.localtime(int(epoch)))

            else:
                result[headers[index]] = data[index].text.strip()
    return result


def clean_fname(fname: str):
    # The below line prevents the error when the file_name starts with ".\" or "./".
    if fname.startswith(".\\") or fname.startswith("./"):
        fname = fname[2:]
    # If file_name is an absolute path, then the below line does nothing.
    fname = os.path.join(os.getcwd(), fname)
    return fname


if __name__ == "__main__":
    program_start_time = time.time()
    time_string = time.strftime('%Y%m%d_%H%M%S', time.localtime())

    # Parse arguments
    parser = argparse.ArgumentParser(description="BOJ Crawler")
    parser.add_argument("query", help="Path to the query configuration file")
    parser.add_argument("-o", "--output", help="Path to the output file")
    args = parser.parse_args()

    # Retrieve the values of the arguments
    query_path = args.query
    output_path = args.output

    # ===== COMMENT OUT THIS SECTION TO DEBUG =====
    # Read yaml file
    fname = clean_fname(query_path)
    with open(fname, "r", encoding="utf-8") as f:
        query = yaml.load(f, Loader=yaml.FullLoader)
    users = query["user"]
    problems = query["problem_id"]
    logger = Logger(users, problems)

    # Process the query
    i = 0
    total = len(problems) * len(users)
    for pid in problems:
        for u in users:
            uid = u["id"]
            print(f"Crawling problem [ {pid} ] for user [ {uid} ]")
            html = get_html(pid, uid)
            results: List[Dict] = crawl_table(html)
            logger.push_status(pid, uid, results)
            # Time delay
            i += 1
            prob = random.randint(0, 100)
            human_time = 4 + random.randint(0, 60 if prob < 10 else 3)
            print(
                f"\tSleeping for {human_time} seconds... [{i}/{total}: {100 * (i) / total:.0f}%] ({time.time() - program_start_time:.0f}s)"
            )
            time.sleep(human_time)
    # =============================================

    # DEBUG
    import pickle
    DEBUG_LOGGER_PATH = os.path.join("temp", f"logger_{time_string}.pkl")
    # DEBUG: Save as pickle file
    with open(DEBUG_LOGGER_PATH, "wb") as f:
        pickle.dump(logger, f)
    # # DEBUG: Load from pickle file
    # with open(DEBUG_LOGGER_PATH, "rb") as f:
    #     logger: Logger = pickle.load(f)

    # print(f"Users: {logger.user_list}")
    # print(f"Problems: {logger.problem_list}")
    # print("Status:")
    # import pprint
    # pprint.pprint(logger.status)

    # Remake into a html file
    logger.make_report()

    # Output file
    o_name = clean_fname("report.html" if output_path is None else output_path)
    # Add timestamp to the file name
    o_name = o_name.replace(".html", f"_{time_string}.html")
    with open(o_name, "w", encoding="utf-8") as f:
        f.write(logger.html)
    print(f"Report saved to: {o_name}")
