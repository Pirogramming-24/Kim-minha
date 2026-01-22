# 나만의 AI 사이트 (Django)

---
## 사용 모델

<!-- Helsinki-NLP/opus-mt-en-ko
### 1. facebook/nllb-200-distilled-600M
-**태스크**: Translation (번역)
-**입력 예시**Abundant faunal evidence links evolutionary patterns with palaeoenvironmental change as a principal underlying force1. Many of the earlier hominin taxa recognized today are found in the Afar, but Paranthropus has been conspicuously absent from the region.
-**출력 예시**풍부한 생물학적 증거는 진화 패턴과 환경 변화를 근본적인 요인으로 연결하고 있습니다1. 오늘날 알려진 초기 호미인 taxon의 많은 것들은 아파르에서 발견됩니다. 하지만 파란트로푸스는 분명히 그 지역에서 사라졌습니다.
- 실행 화면 예시:
-->

<!-- sshleifer/distilbart-cnn-12-6
### 2. facebook/bart-large-cnn
-**태스크**: Summarization (요약)
-**입력 예시**
The Afar depression in northeastern Ethiopia contains a rich palaeontological and archaeological record, which documents 6 million years of human evolution. Abundant faunal evidence links evolutionary patterns with palaeoenvironmental change as a principal underlying force1. Many of the earlier hominin taxa recognized today are found in the Afar, but Paranthropus has been conspicuously absent from the region.
-**출력 예시**
The Afar depression in northeastern Ethiopia contains a rich palaeontological and archaeological record . Many of the earlier hominin taxa recognized today are found in the Afar . Paranthropus has been conspicuously absent from the region .
- 실행 화면 예시:
-->

<!--Qwen/Qwen2.5-1.5B-Instruct
### 3. distilbert-base-uncased-finetuned-sst-2-english
-**태스크**: Sentiment Analysis (글쓰기))
-**입력 예시**The Afar
-**출력 예시**Afar is the largest depression in Ethiopia's history . It is also known as a depression in the Afar Depression . Ethiopia is one of the largest depressions in the world, with a population of more than 100,000 .
- 실행 화면 예시:
-->

---
## 로그인 제한(Access Control)

- 비로그인 사용자는**1개 탭만 사용 가능**
- 제한 탭 접근 시**“로그인 후 이용해주세요” alert 후 로그인 페이지로 이동**
- 로그인 성공 시**원래 페이지로 복귀(next)**

---
## 구현 체크리스트

- [✅] 탭 3개 이상 + 각 탭 별 URL 분리
- [✅] 각 탭: 입력 → 실행 → 결과 출력
- [✅] 에러 처리: 모델 호출 실패 시 사용자에게 메시지 표시
- [✅] 로딩 표시(최소한 “처리 중…” 텍스트라도)
- [✅] 요청 히스토리 5개
- [✅]`.env` 사용 (토큰/API Key 노출 금지)
- [✅]`README.md`에 모델 정보/사용 예시/실행 방법 작성 후 GitHub push

### 로그인 제한 체크
- [✅] 비로그인 사용자는 1개 탭만 접근 가능
- [✅] 제한 탭 접근 시 alert 후 로그인 페이지로 redirect
- [✅] 로그인 성공 시 원래 페이지로 복귀(next)