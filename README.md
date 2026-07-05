# Native Function Calling Chatbot Demo

본 프로젝트는 기존의 단순 텍스트 병합(String Concatenation) 방식의 한계를 극복하고, Google Gemini의 **Native Function Calling** 아키텍처를 도입하기 위해 제작된 테스트/데모 프로젝트입니다.

## 🚀 주요 특징 (Features)

1. **Native Tool Calling Architecture (Loop 체계)**
   - 대화 기록을 단순 문자열이 아닌 엄격한 JSON 기반의 `contents` 배열로 관리합니다.
   - LLM이 툴을 호출(`function_call`)하면, 백엔드 로직을 실행한 뒤 결과를 반환(`function_response`)하여 다시 LLM을 호출하는 자동화된 루프가 구현되어 있습니다 (`backend/agent/engine.py`).

2. **최신 논문 기반 라우팅 및 동적 툴 선택 (Dispatcher)**
   - 모든 툴을 프롬프트에 무작정 집어넣는 대신, 사용자의 발화 의도(Intent)를 파악해 **필요한 툴 스키마만 동적으로 주입**합니다 (`backend/agent/dispatcher.py`).
   - 토큰 낭비와 할루시네이션(환각)을 방지하는 모던 에이전트 설계 패턴입니다.

3. **초고속 응답 최적화 (WebSockets)**
   - FastAPI의 WebSocket을 활용하여 클라이언트와 서버 간 지속적인 연결을 유지합니다.
   - 도구(Tool) 실행 중에 "검색 중...", "실행 완료"와 같은 상태 메시지를 프론트엔드로 즉각 스트리밍하여 체감 대기 시간을 크게 단축했습니다.

4. **Agentic Self-Correction (자가 복구 로직)**
   - API나 도구에서 에러가 발생하면, LLM이 에러 메시지를 읽고 스스로 파라미터를 교정하여 재시도(Retry)하는 강력한 회복 탄력성을 갖추고 있습니다.

5. **실시간 텍스트 스트리밍 (Real-time Streaming)**
   - 답변이 모두 생성될 때까지 기다리지 않고, 생성되는 즉시 타이핑 효과와 함께 UI에 부드럽게 렌더링됩니다.

6. **Agentic State Tracking Dashboard (라이브 고객 상태 티켓)**
   - 단순 문답을 넘어, LLM이 스스로 고객의 의도(Intent), 주문번호, 긴급도 등을 트래킹하여 우측 대시보드에 실시간으로 업데이트합니다. 

7. **라우터 LLM 동적 구성 (Router Configuration)**
   - 설정 탭을 통해 대화용 메인 LLM뿐만 아니라, 의도 파악과 도구를 선택하는 라우터(Router) 전용 LLM 모델을 자유롭게 변경할 수 있습니다.

8. **완벽한 관심사 분리 (Clean Architecture)**
   - 라우터(API), 에이전트 루프 로직(Agent), 실제 백엔드 비즈니스 로직(Tools)이 철저하게 분리된 폴더 구조를 가집니다.

9. **Premium UI/UX Design**
   - 글래스모피즘(Glassmorphism)과 부드러운 애니메이션, 모던한 다크 테마를 적용한 수준 높은 프론트엔드 환경을 제공합니다.

---

## 🛠 코드 구조 (Directory Structure)

```text
gemini-function-calling-demo/
├── .env                       # 환경 변수 (GCP 및 Gemini 인증)
├── requirements.txt           # 파이썬 의존성 패키지
├── backend/
│   ├── main.py                # FastAPI 엔트리포인트 (웹서버 실행)
│   ├── api/
│   │   └── chat_router.py     # WebSocket 연결 및 메시지 라우팅
│   ├── agent/
│   │   ├── engine.py          # Gemini 멀티턴 세션 및 Function Calling 루프
│   │   ├── dispatcher.py      # 사용자 의도 파악 및 동적 툴셋 할당
│   │   ├── schemas.py         # 데이터 스키마
│   │   └── prompts.py         # 시스템 프롬프트 분리
│   ├── tools/
│   │   ├── manual_tools.py    # (가상) DB 규정 조회, 주문 상태 조회 로직
│   │   └── tool_registry.py   # Gemini 스키마 선언 및 파이썬 함수 맵핑
│   └── core/
│       └── config.py          # 설정 로드 모듈
└── frontend/
    ├── index.html             # 채팅 메인 레이아웃 UI
    ├── css/style.css          # 프리미엄 다크 테마 디자인 적용
    └── js/app.js              # WebSocket 통신 로직 및 상태 업데이트
```

---

## 💻 실행 방법 (How to Run)

### 1. 환경 설정 및 API Key 등록
본 프로젝트 디렉토리로 이동한 뒤, Conda 가상 환경을 생성하고 패키지를 설치합니다.

```bash
# 디렉토리 이동
cd gemini-function-calling-demo

# .env 파일 생성 및 API 키 입력
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```
*(주의: 소스 코드 상에 절대 경로가 하드코딩되거나 API 키가 직접 노출되지 않도록, 모든 환경 변수는 `.env`에서만 관리됩니다.)*

```bash
# 아나콘다 가상환경 생성 (예: 파이썬 3.10)
conda create -n gemini-demo python=3.10 -y

# 가상환경 활성화
conda activate gemini-demo

# 패키지 설치
pip install -r requirements.txt
```

### 2. 서버 실행
가상환경이 활성화된 상태에서 FastAPI 백엔드 서버를 구동합니다.
```bash
# 실행 전 가상환경 활성화가 안 되어 있다면: conda activate gemini-demo
python -m backend.main
```
서버가 정상적으로 실행되면 `Uvicorn running on http://0.0.0.0:8001` 형태의 메시지가 출력됩니다.

### 3. 접속 및 테스트
웹 브라우저를 열고 다음 주소에 접속합니다.
👉 **http://localhost:8001**

**테스트 예시 명령어:**
- "환불규정 알려줘" (정책 안내 툴 호출 테스트)
- "주문한 상품이 너무 안와서 화가 나네요. 내 주문번호는 123입니다." (자가 복구 테스트 및 상태 트래킹 대시보드 업데이트 시연)

좌측 채팅창에서 실시간 타이핑 스트리밍이 진행되며, 우측 대시보드에서는 AI가 추출한 고객의 티켓 상태가 깜빡거리며 업데이트됩니다. 또한 "Logs" 탭에서 모든 도구 실행과 자가 복구 과정의 JSON 원본을 투명하게 확인하실 수 있습니다.