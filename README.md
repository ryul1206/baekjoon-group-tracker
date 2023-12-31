# baekjoon-group-tracker

This crawler is designed for the Korean coding problem platform, [BOJ (Baekjoon Online Judge)](https://www.acmicpc.net/).

스터디 그룹을 관리하는데 도움이 되는 크롤러입니다.

- 스터디 멤버 명단과 같이 풀기로한 문제의 목록을 입력하면, [백준 채점현황](https://www.acmicpc.net/status)에서 자동으로 취합해서 알려줍니다.
- 백준 그룹에도 채점 현황이 있지만, 정렬이나 필터링 기능이 부족하여 골라 보기가 불편하기 때문에 만들었습니다.
- 백준 온라인 저지는 처음엔 웹 스크래핑을 금지하지 않다가 몇 년 전부터 금지하게 되었습니다. 하지만 API 제공은 여전히 되지 않고 있기 때문에, 서버에 무리가 가지 않도록 5초 이상 넉넉한 딜레이를 주고 사용해주세요. ([참조1](https://www.acmicpc.net/board/view/2308), [참조2](https://help.acmicpc.net/rule))
- 악의적인 사용을 하지 맙시다. 악의적인 사용에는 다음과 같은 것들이 있습니다.
  - 수시로 크롤링하여 서버에 부하를 주는 행위
  - 많은 학생이나 많은 문제를 한꺼번에 요청하여 서버에 부하를 주는 행위
  - 모르는 사람의 아이디를 입력하여 스토킹하는 행위
  - 기타 사람의 시간당 서버요청에 비해 많은 요청을 하는 행위
  - 기타 타인에게 피해를 입히는 행위

## 사용법

먼저, `query.yaml`에 스터디 멤버 명단과 같이 풀기로한 문제의 목록을 입력합니다. `name` 필드는 비어 있어도 됩니다.

```yaml
user:
  - id: user_id_1
    name: 하나
  - id: user_id_2
    name: 둘이
  - id: user_id_3
    name: 서이
problem_id:
  - 1000
  - 1003
  - 28304
```

그리고, `crawler.py`를 실행합니다.

```sh
python3 crawler.py query.yaml
```

정리된 채점 현황이 `result_{일시}.html`에 저장됩니다.
만약 다른 이름이나 경로로 저장하고 싶다면, `-o` 옵션을 사용합니다.
`_{일시}` 정보는 항상 부여되도록 작성하였기에, 아래 명령은 실제론 `week1_{일시}.html`로 저장됩니다.

```sh
python3 crawler.py query.yaml -o ./folder/week1.html
```

## 필요 라이브러리

```sh
pip3 install beautifulsoup4
pip3 install pyyaml
```
