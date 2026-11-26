# Pitch script (English, 6 minutes) — draft v1 (2026-11-26, 분량·주장 범위 정리)

- 분량과 시간: 아래 줄의 단어 수는 `docs/review/local_fix/count_words.py`로 센 값이다. 분당 135단어 계산값일 뿐, **소리 내어 읽어 잰 시간이 아니다.** 넘치면 4번의 노드 설명과 5번의 판정 나열을 먼저 줄인다.
- 슬라이드 기준: 2026-11-26 23:44에 제출한 발표 PDF(영어 10장, 간소화판). 화면에서 90일 패널, 규칙 문단, 84/84 패널, 바닥글이 빠졌으므로 **90일 규칙과 84회 실행은 말로만 전달된다.**
- 결과 숫자의 기준: 설정 #7(제출 설정), 2026-11-26 실행. 제출 10건 두 번과 경계값 21건 세 번, 네 키를 Studio 응답 원문에서 읽어 코드로 대조했다.
- 발음 메모: demurrage = 디-머-리지 /dɪˈmʌrɪdʒ/, laytime = 레이-타임, BPVOY4 = "B-P-voy four".

---

## Slide 1 — Title

Good afternoon. I'm Yena Chang, team TimeBar.

Every crude oil cargo ends with paperwork. When a tanker waits longer than agreed, the shipowner sends the cargo owner a bill for the delay. That bill is a demurrage claim. My workflow checks the evidence behind that claim, before anyone pays.

## Slide 2 — How one missing signature erases the whole claim

Start with the industry. Aramco exported six point three million barrels of crude a day in 2025. Bahri, the exclusive carrier of Aramco's delivered crude, earned four point seven billion riyals from the Aramco group last year. And Bahri's prospectus defines demurrage as the rate Aramco's subsidiary pays when loading or discharge runs late.

That payment runs on paperwork. Under the BPVOY4 charter party, the claim and all supporting documents must arrive within ninety days after discharge. If not, the charterer is released from liability.

Courts enforce this. In 2007, a claim of one hundred and fourteen thousand dollars was barred over an unsigned pumping log. In 2015, three hundred and sixty-four thousand, over port logs that were never sent. In 2020, fifty-six thousand, over two bills of lading.

In each case the charterer found the gap. That check is the task I automate.

## Slide 3 — How?

The user is the claims handler on the charterer's side. In mentoring here, I learned two things. A dedicated team handles these claims today. And for that team to adopt automation, it must match their decisions without error. So I built this around verification.

A claim arrives as one bundle of up to six kinds of document. The handler asks four questions. Is everything here? Is the pumping log signed? Did it arrive in time? Do the times agree?

The money calculation stays with the handler.

## Slide 4 — The handler's steps, one node each

Each step of that work is one node.

Parse reads every page, including scans. Classify splits the bundle into six document types. Six Extract nodes pull only what is needed: dates, signatures, and whether the page is readable. Merge puts one claim into one record. One Instruct node decides, and four more draft the follow-up document.

I started from Use Case card U038, container demurrage, and changed the question from the amount to the evidence.

## Slide 5 — How are the decisions structured?

There are four decisions, checked in a fixed order.

First, review needed: something is unreadable, belongs to another vessel, or does not match. Second, time-bar risk: the claim arrived after the deadline. Third, request documents: something is missing or unsigned. Only when every check passes: clear for payment review.

The workflow never says "reject". A time-bar defence has also failed in court, so that call belongs to a person.

## Slide 6 — Reliability design

Three choices make this reliable.

One. A covered or blurred value is never filled in. The case goes to review.

Two. When the contract is silent, the workflow does not assume. An unsigned pumping log with a protest attached goes to a person, because BPVOY4 does not say the protest is enough.

Three. The model does no arithmetic. It reads two dates from the receipt record and compares them.

I tested this with ten claim packages, fifty-one documents, covering all four decisions. The answer key comes from rule code, not from a model.

## Slide 7 — Studio results: all 10 match

Here is what happened in Studio.

On the first full run, nine of ten were right. You can see the one red mark: set three. I found the cause in the extraction step, fixed it, and all ten matched.

Then I built twenty-one new packages the workflow had never seen. They broke it again: it passed a claim with the wrong claim number, and it invented a vessel name. I tightened the decision prompt and tested every version against every case.

The version I submitted ran eighty-four times: the ten packages twice, the twenty-one three times. All eighty-four matched, on the decision, the missing-document list, the claim number and the vessel name.

## Slide 8 — Built so the handler can take the next step right away

The output is not only a label. For each decision, the handler gets the next document: a draft letter to the owners listing what is missing, a short memo with the two dates or values that disagree, or a memo of what was confirmed.

On the screen is a real run: an empty terminal signature line on the left, the draft letter on the right.

## Slide 9 — Close

To sum up: one missing signature can erase a claim. TimeBar checks the evidence in one pass, hands over when it is not sure, and prepares the next step.

Thank you. I'm happy to take your questions.

---

## Q&A — 준비할 답 (초안)

**Q. Isn't this a shipping problem, not an energy problem?**
The documents are produced at the terminal during cargo operations: the notice of readiness, the statement of facts, the pumping log. Bahri's prospectus defines demurrage under its contract with Bolanter, a wholly-owned Aramco subsidiary, as the rate Bolanter pays when loading or discharge runs late. And Aramco Trading describes itself as a leading global charterer. So the paperwork risk sits on the energy company's side of the contract.

**Q. Does this fit where Aramco is going?**
Aramco's 2025 sustainability report says it has deployed almost five hundred AI use cases company-wide, and that about half of the value realized from its technology investments was linked to AI. The direction is theirs, and this workflow is one concrete candidate: paperwork at the end of every crude cargo.

**Q. Is there a sustainability angle?**
The value here is governance: control over payments and deadlines, with a person deciding every unclear case. That is the same discipline the report describes for operations.

**Q. Did you confirm how claims handlers work today?**
A mentor from the industry confirmed that companies have a dedicated team for this. My next step is to sit with that team and tune the checks to their routine.

**Q. Why not calculate the demurrage amount too?**
In the cases I showed, the claims were not lost on the amount. They were lost on missing documents and deadlines. I chose the part where a mistake costs the whole claim, and where the answer can be checked against a clear rule.

**Q. Charter parties differ. Does this only work for BPVOY4?**
Yes, the deadline rule in this version follows BPVOY4, clause 20.1. The list of five required documents is my team's intake standard for a fictional charterer; the contract itself says "all supporting documentation" and does not list them. Changing the form means changing the criteria in one Instruct node and the receipt record, not the whole workflow.

**Q. How do you know the model reads a signature correctly?**
Two test cases have an empty terminal signature line on the pumping log. In every run, both got the decision that an unsigned log should get. The decision uses the terminal countersignature, which is the signature the contract asks for.

**Q. Why is the deadline date on a document instead of being calculated?**
A language model can miscount days. A claims register already records the date received and the deadline. Reading two dates and comparing them is more reliable than asking the model to add ninety days.

**Q. Eighty-four of eighty-four. Is that accuracy?**
It is every run on the shipped version: claim number, vessel name, decision and missing-document list, read from Studio's raw output and compared in code, across thirty-one different packages built to break the workflow. I also read the reason text and found no wrong reason.

**Q. Four of your ten cases end in "review needed". Is that automation?**
Those four are the hard cases on purpose. Even then the handler gets the reason and the place to look. The other six are sorted without anyone opening six documents.

**Q. How did you use AI tools in building this?**
I set the criteria and made the decisions. Claude Code collected sources, generated the test documents and wrote the comparison code. Upstage Studio does the reading and judging. I copied the Studio results by hand. I checked Claude's claims against the original judgments, and several of its first claims were wrong, so I corrected them.

**Q. What would you do next?**
Ask a real claims team which document problem is most common, and add the charter party recap as a seventh document so special terms can be checked.
