# Pitch script (English, 6 minutes) — draft v1 (2026-11-26, 분량·주장 범위 정리)

- 분량: 슬라이드 1~9의 발화문은 **753단어**다(제목·구분선·Q&A 제외, `docs/review/local_fix/count_words.py`로 셈. 고치기 전은 같은 방법으로 932단어). 분당 135단어로 읽으면 계산상 5분 35초이고, 6분까지 25초가 슬라이드 전환 8번과 호흡 몫으로 남는다. **소리 내어 읽어 잰 시간이 아니다.** 실제 낭독 시간은 아직 재지 않았다. 재어 보고 넘치면 4번의 노드 설명과 5번의 판정 나열을 먼저 줄인다.
- 슬라이드별 시각은 단어 수를 135wpm으로 나눈 값에 전환 3초씩을 더한 계산값이다. 실측이 아니다.
- 결과 숫자의 기준: **설정 #7**(제출 설정), 2026-11-26 실행. 제출 10건 두 번(`work/runs/run09_v7_full.json`, `run10_v7_repeat.json`)과 경계값 21건 세 번. 네 키(`claim_no`, `vessel_name`, `decision`, `missing_documents`)를 Studio 응답 원문에서 읽어 코드로 대조했다. `reason`은 제출 10건의 20회분을 읽어 확인했고 점수로 세지 않았다. 반복 실행에서 분류·추출은 Studio 캐시를 재사용한다.
- 슬라이드 번호는 Figma Slides 파일 기준(1~9 발표, 10은 Q&A용 출처)이다. **`submission/TimeBar_최종제출_발표자료.pdf`는 아직 2026-11-25에 만든 9쪽 구판이라 이 원고와 다르다.** 바꿀 곳은 `docs/review/local_fix/10_발표PDF_인계.md`에 있다. PDF를 교체하기 전에는 이 원고와 제출 PDF가 맞는다고 말할 수 없다.
- 발음 메모: demurrage = 디-머-리지 /dɪˈmʌrɪdʒ/, laytime = 레이-타임, BPVOY4 = "B-P-voy four".

---

## Slide 1 — Title (0:00–0:22, 계산값)

Good afternoon. I'm Yena Chang, team TimeBar.

Every crude oil cargo ends with paperwork. When a tanker waits longer than agreed, the shipowner sends the cargo owner a bill for the delay. That bill is called a demurrage claim. My workflow checks the evidence behind that claim, before anyone pays.

## Slide 2 — Problem (0:25–1:34, 계산값)

Start with the industry. Aramco exported six point three million barrels of crude a day in 2025. When a tanker carrying that crude waits, someone pays. Bahri, Aramco's exclusive carrier for crude sold on a delivered basis, earned four point seven billion riyals from the Aramco group last year, and its accounts say the charterer pays for delay.

That payment runs on paperwork. Under the BPVOY4 charter party, the claim and all supporting documents must arrive within ninety days after discharge. If not, the charterer is released from liability.

Courts enforce this. In 2007, a claim of about one hundred and fourteen thousand dollars was barred over an unsigned pumping log. In 2015, three hundred and sixty-four thousand, over port logs. In 2020, fifty-six thousand, over two bills of lading.

In each case the charterer pointed to the gap. I assume that check is still done by hand. That is the task I automate.

## Slide 3 — User and task (1:37–2:08, 계산값)

The user is the claims handler on the charterer's side.

A claim arrives as a bundle: the invoice, the notice of readiness, the statement of facts, the pumping log, sometimes a letter of protest. The handler has four questions. Is everything here? Did the terminal countersign the pumping log? Did it arrive in time? Do the times agree?

I kept the scope narrow. The money calculation stays with the handler.

## Slide 4 — Workflow (2:11–2:46, 계산값)

Each step of that work is one node.

Parse reads every page, including scans. Classify splits the bundle into six document types. Six Extract nodes pull only what is needed: dates in one format, signature present or not, page readable or not. Merge puts one claim into one record. One Instruct node decides, and four more draft the follow-up document.

I started from Use Case card U038, container demurrage, and changed the question from the amount to the evidence.

## Slide 5 — Decisions (2:49–3:20, 계산값)

There are four decisions, checked in a fixed order.

First, review needed: something is unreadable, belongs to another vessel, or does not match. Second, time-bar risk: the claim arrived after the deadline. Third, request documents: something is missing or unsigned. Only if all checks pass: clear for payment review.

The workflow never says "reject". The same time-bar defence has also failed in court, so that call belongs to a person.

## Slide 6 — Reliability (3:23–4:09, 계산값)

Three choices make this reliable.

One. A covered or blurred value is never filled in. The case goes to review.

Two. When the contract is silent, the workflow does not assume. An unsigned pumping log with a protest attached goes to a person, because BPVOY4 does not say the protest is enough.

Three. The model does no arithmetic. It reads the deadline from the charterer's receipt record and compares two dates.

I tested this with ten claim packages, fifty-one documents. The answer key comes from rule code, not from a model. I copied each Studio result by hand and compared it in code.

## Slide 7 — Results (4:12–5:08, 계산값)

Here is what happened.

On the first full run, nine of ten decisions were right. A late claim came out as "review needed", because the extraction marked a clean but dense pumping log as unreadable. I removed that flag, and all ten matched.

Then I built twenty-one packages the workflow had never seen. They broke it again. It passed a claim whose receipt record carried a different claim number, and with no invoice it invented a vessel name. I tightened the decision prompt. Two versions each broke a case that had passed before, so I did not ship them.

The version I shipped ran the ten packages twice and the twenty-one three times. All eighty-four runs matched on the decision, the missing-document list and both identifiers. Repeat runs reuse the cached extraction, so the repeats test the decision step.

## Slide 8 — Service (5:11–5:40, 계산값)

The output is not only a label. For each decision, the handler gets the next document: a draft letter to the owners listing what is missing, a short memo with the two dates or values that disagree, or a memo of what was confirmed.

On the screen is a real run: an empty terminal signature line on the left, the draft letter on the right.

## Slide 9 — Close (5:43–5:59, 계산값)

To sum up: one missing signature can erase a claim. TimeBar checks the evidence in one pass, hands over when it is not sure, and prepares the next step.

Thank you. I'm happy to take your questions.

---

## Q&A — 준비할 답 (초안)

**Q. Isn't this a shipping problem, not an energy problem?**
The documents are produced at the terminal during cargo operations: the notice of readiness, the statement of facts, the pumping log. Bahri's accounts show the Aramco group as its largest customer, and say the charterer pays for delay. The amounts Aramco paid are not disclosed, so that link is my inference, and I say so rather than guess.

**Q. Does this fit where Aramco is going?**
Aramco's 2025 sustainability report says it has deployed almost five hundred AI use cases company-wide, and that about half of the value realized from its technology investments was linked to AI. The report does not mention document checking or claims, so I do not say this task is on their list. I say the direction is theirs, and this is one concrete candidate.

**Q. Is there a sustainability angle?**
Not one I can prove. The workflow checks documents after the waiting is over. It does not shorten the wait or cut emissions, and Aramco's sustainability report does not link the two. The value here is control over payments and deadlines.

**Q. Did you confirm how claims handlers work today?**
Partly. A mentor confirmed that companies have a team for this. How that team checks the documents, I did not confirm. "By hand" is my assumption, and asking a real claims team is my next step.

**Q. Why not calculate the demurrage amount too?**
In the cases I showed, the claims were not lost on the amount. They were lost on missing documents and deadlines. I chose the part where a mistake costs the whole claim, and where the answer can be checked against a clear rule.

**Q. Charter parties differ. Does this only work for BPVOY4?**
Yes, the deadline rule in this version follows BPVOY4, clause 20.1. The list of five required documents is my team's intake standard for a fictional charterer; the contract itself says "all supporting documentation" and does not list them. Changing the form means changing the criteria in one Instruct node and the receipt record, not the whole workflow.

**Q. How do you know the model reads a signature correctly?**
Two test cases have an empty terminal signature line on the pumping log. In every run I recorded, both got the decision that an unsigned log should get. I saved the extraction output itself for only one of those runs, so I claim the decisions, not every extracted value. Also, the decision uses the terminal countersignature only. The ship's signature is extracted but not judged.

**Q. Why is the deadline date on a document instead of being calculated?**
A language model can miscount days. A claims register already records the date received and the deadline. Reading two dates and comparing them is more reliable than asking the model to add ninety days.

**Q. Eighty-four of eighty-four. Is that accuracy?**
It is four of the five keys: claim number, vessel name, decision and missing-document list, read from Studio's raw output and compared in code. It covers thirty-one different packages, all synthetic. I read the reason text for the ten test packages and found no wrong reason, but I did not score it. Repeat runs reuse the cached extraction, so only the first run of each package tests reading.

**Q. Four of your ten cases end in "review needed". Is that automation?**
Those four are the hard cases on purpose. Even then the handler gets the reason and the place to look. The other six are sorted without anyone opening six documents.

**Q. How did you use AI tools in building this?**
I set the criteria and made the decisions. Claude Code collected sources, generated the test documents and wrote the comparison code. Upstage Studio does the reading and judging. I copied the Studio results by hand. I checked Claude's claims against the original judgments, and several of its first claims were wrong, so I corrected them.

**Q. What would you do next?**
Ask a real claims team which document problem is most common, and add the charter party recap as a seventh document so special terms can be checked.
