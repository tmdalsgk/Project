본 프로젝트는 Pygame 기반 지뢰찾기(Minesweeper) 게임입니다.
--------------------------------------------------------------------------------------------------------
기본 기능 1) 좌클릭 (Left Click)
--------------------------------------
선택한 셀을 열기(reveal) 

지뢰가 있는 셀 → 게임 오버

숫자 셀 → 주변 지뢰 개수 표시

빈 셀 → 인접한 빈 셀까지 자동 연쇄 오픈

첫 좌클릭 시점부터 타이머가 시작

게임이 종료되었거나 일시정지 상태에서는 동작하지 않습니다.

-----------------------------------------------------------------------------------------------------------------------
기본 기능 2) 우클릭 (Right Click)
------------------------------------------------
클릭하려고 하는 셀이 지뢰라고 추정할 때 우클릭 시 열기 대신 깃발을 표시 

이미 열린 셀에는 우클릭 불가

----------------------------------------------------------------------------------------------------
주요 기능 1) 숫자 색 표시 기능
------------------------------------------
좌클릭하여 칸에 숫자 생성 시 숫자마다 색깔이 다르게 표시

<img width="546" height="598" alt="image" src="https://github.com/user-attachments/assets/7a14db74-0b10-476d-ab0d-b6e2fe17e486" />

주요 기능 2) 난이도 설정 
----------------------------------
키보드 입력으로 난이도 변경 가능

1 : EASY

2 : MEDIUM

3 : HARD

난이도에 따라 보드 크기 / 지뢰 개수 / 화면 크기가 자동 조정됨

현재 난이도가 상단 헤더 중앙에 직관적으로 표시

<img width="358" height="400" alt="image" src="https://github.com/user-attachments/assets/97a2a079-d72b-4c73-a15d-72343ecddf16" />
<img width="549" height="618" alt="image" src="https://github.com/user-attachments/assets/7342d0de-fce3-40e1-84ae-9c7a50958fae" />
<img width="986" height="739" alt="image" src="https://github.com/user-attachments/assets/f19c6a87-99cf-4ce4-a8c0-a3aaa6fe400b" />

주요 기능 3) 힌트 기능
---------------------------------------
H 키를 누르면 지뢰가 아닌 안전한 칸 1개를 자동으로 공개

게임당 1회만 사용 가능

힌트 사용 여부가 상단 헤더에 Hint: 0/1, Hint: 1/1 형태로 표시

<img width="546" height="598" alt="image" src="https://github.com/user-attachments/assets/7a14db74-0b10-476d-ab0d-b6e2fe17e486" />
<img width="546" height="575" alt="image" src="https://github.com/user-attachments/assets/33b7a251-07bc-4341-a7f1-406e0ef0210b" />

주요 기능 4) 하이 스코어 저장 및 표출 기능
---------------------------------------------------
highscore.txt 파일을 이용히여 최고 기록 저장 및 로드 기능을 구현

주요 기능 5) 타이머 표기 기능
--------------------------------------------
게임 진행 시간을 실시간으로 확인할 수 있도록 상단에 타이머 기능 표기

<img width="546" height="575" alt="image" src="https://github.com/user-attachments/assets/33b7a251-07bc-4341-a7f1-406e0ef0210b" />
<img width="541" height="587" alt="image" src="https://github.com/user-attachments/assets/cac94d73-510d-4fa6-8e59-c8e692d59011" />


