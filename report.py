from typing import List, Dict
from bs4 import BeautifulSoup, Tag


def make_thead(soup: BeautifulSoup, header_data: List[str]) -> Tag:
    thead = soup.new_tag("thead")
    tr = soup.new_tag("tr")
    thead.append(tr)
    for item in header_data:
        th = soup.new_tag("th")
        th.string = str(item)
        tr.append(th)
    return thead


class Logger:
    def __init__(self, user_list: List[Dict], problem_list: List[int]):
        self.user_list = user_list
        self.problem_list = [int(p) for p in problem_list]
        # print(f"User list: {self.user_list}")
        # print(f"Problem list: {self.problem_list}")
        self.status = {p: {u["id"]: None for u in self.user_list} for p in self.problem_list}
        self.summary = {u["id"]: {p: "✖️" for p in self.problem_list} for u in self.user_list}
        # 🟢, 🔶, ✖️
        self.html: str = None

    def push_status(self, problem_id: str, user_id: str, result: List[Dict]):
        self.status[problem_id][user_id] = result

    def user_name(self, user_id: int) -> str:
        for user in self.user_list:
            if user["id"] == user_id:
                return user["name"]
        return None

    def make_report(self):
        self.summary = {u["id"]: {p: "✖️" for p in self.problem_list} for u in self.user_list}

        # BeautifulSoup 객체 생성
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        # 문제별 상세
        h1_tag = soup.new_tag("h1")
        h1_tag.string = "문제별 상세"
        soup.body.append(h1_tag)

        for pid in self.problem_list:
            # 문제 제목
            url = f"https://www.acmicpc.net/problem/{pid}"
            h2_tag = soup.new_tag("h2")
            a_tag = soup.new_tag("a", href=url)
            a_tag.string = f"문제 {pid}"
            h2_tag.append(a_tag)
            soup.body.append(h2_tag)

            # 유저별 테이블
            status_per_user = self.status[pid]
            for uid, rows in status_per_user.items():
                # 유저 이름
                p_tag = soup.new_tag("p")
                p_tag.string = f"{self.user_name(uid)} ({uid})"
                soup.body.append(p_tag)

                # 테이블 생성
                table = self.make_log_table(soup, rows)
                soup.body.append(table)

        # 요약
        h1_tag = soup.new_tag("h1")
        h1_tag.string = "요약"
        soup.body.insert(0, h1_tag)
        table = self.make_summary_table(soup)
        soup.body.insert(1, table)

        # CSS 추가한 최종 HTML
        with open("github-light.css", "r", encoding="utf-8") as f:
            css_content = f.read()
        self.html = f"<style>{css_content}</style><article class='markdown-body'>{soup.prettify()}</article>"

    def make_summary_table(self, soup: BeautifulSoup) -> Tag:
        table = soup.new_tag("table")

        # 테이블 헤더 생성
        header_data = ["멤버", *self.problem_list]
        table.append(make_thead(soup, header_data))

        # 테이블 본문 생성
        tbody = soup.new_tag("tbody")
        table.append(tbody)
        for user_id, summary in self.summary.items():
            tr = soup.new_tag("tr")
            tbody.append(tr)
            # 멤버 이름
            td = soup.new_tag("td")
            td.string = f"{self.user_name(user_id)} ({user_id})"
            tr.append(td)
            # 문제별 결과
            for pid in self.problem_list:
                td = soup.new_tag("td")
                td.string = summary[pid]
                tr.append(td)
        return table

    def make_log_table(self, soup: BeautifulSoup, rows: List) -> Tag:
        table = soup.new_tag("table")

        # 테이블 헤더 생성
        header_data = ["제출 번호", "아이디", "문제", "결과", "메모리", "시간", "언어", "코드 길이", "제출한 시간"]
        table.append(make_thead(soup, header_data))

        # 테이블 본문 생성
        tbody = soup.new_tag("tbody")
        table.append(tbody)
        for submission in rows:
            tr = soup.new_tag("tr")
            tbody.append(tr)
            for key in header_data:
                td = soup.new_tag("td")
                td.string = submission[key]
                tr.append(td)
            # Summary 업데이트
            self.update_summary(submission["문제"], submission["아이디"], submission["결과"])

        return table

    def update_summary(self, pid, uid, result):
        pid = int(pid)
        # print(f"pid: {pid}, uid: {uid}, result: {result}")
        # print(f"summary: {self.summary[uid]}")
        if self.summary[uid][pid] == "🟢":
            return
        if result == "맞았습니다!!":
            self.summary[uid][pid] = "🟢"
        else:
            self.summary[uid][pid] = "🔶"
