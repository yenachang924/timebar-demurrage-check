# Pitch script (English, 6 minutes) — draft v0

- 목표 길이: 6분. 2번과 7번 슬라이드에 내용을 더해 원고가 약 900단어가 됐다. 분당 135단어로는 6분 40초쯤이라 넘친다. 소리 내어 읽어 시간을 재고, 넘치면 4번(노드 설명)과 6번(세 번째 항목)을 줄인다.
- 7·8번 슬라이드는 2026-11-25 Studio 실행 결과로 채웠다. 문서나 설정을 바꿔 다시 돌리면 숫자를 고친다.
- 슬라이드 번호는 Figma Slides 파일 기준(1~9 발표, 10은 Q&A용 출처). 같은 원고가 각 슬라이드의 발표자 노트에 들어 있다.
- 발음 메모: demurrage = 디-머-리지 /dɪˈmʌrɪdʒ/, laytime = 레이-타임, BPVOY4 = "B-P-voy four".

---

## Slide 1 — Title (0:00–0:25)

Good afternoon. I'm Yena Chang, team TimeBar.

Every crude oil cargo ends with paperwork. When a tanker waits longer than agreed, the shipowner sends the cargo owner a bill for the delay. That bill is called a demurrage claim. My workflow checks the evidence behind that claim, before anyone pays.

## Slide 2 — Problem (0:25–1:25)

Start with the industry. Aramco exported six point three million barrels of crude a day in 2025. When a tanker carrying that crude waits, someone pays. Bahri, the exclusive carrier of the crude Aramco sells on a delivered basis, earned four point seven billion riyals from the Aramco group last year, and its accounts say the charterer pays for delay beyond the agreed time.

That payment runs on paperwork, and the paperwork is a risk. Under the BPVOY4 charter party, the claim and all supporting documents must arrive within ninety days after discharge. If not, the charterer is released from liability.

Courts enforce this. In 2007 a claim of one hundred and fourteen thousand dollars was barred over an unsigned pumping log. In 2015, three hundred and sixty-four thousand, over a port log and time sheets. In 2020, fifty-six thousand, over two bills of lading.

In each case it was the charterer who pointed to the gap. Today that check is done by people, document by document. That is the task I automate.

## Slide 3 — User and task (1:25–2:05)

The user is the claims handler on the charterer's side.

A claim arrives as a bundle: the invoice, the notice of readiness, the statement of facts, the pumping log, sometimes a letter of protest. The handler checks four things by eye. Is everything here? Is it signed? Did it arrive in time? Do the times agree?

I kept the scope narrow on purpose. The workflow checks the evidence. The money calculation stays with the handler.

## Slide 4 — Workflow (2:05–2:55)

I turned each step of the handler's work into one node.

Parse reads every page, including scans. Classify splits the bundle into six document types, and sends anything else to "Other". Six Extract nodes pull only what is needed: dates in one format, whether a signature is present, and whether the page is readable. Merge puts one claim into one record. Then one Instruct node makes the decision, and four more draft the follow-up document.

I started from Use Case card U038, container demurrage. That card recalculates the amount. I changed the question to: is the evidence complete, signed, on time and consistent? Because that is where tanker claims are won or lost.

## Slide 5 — Decisions (2:55–3:35)

There are four possible decisions, checked in a fixed order.

First, review needed: something is unreadable, belongs to another vessel, or does not match. Second, time-bar risk: the claim arrived after the deadline. Third, request documents: something is missing or unsigned. And only if all checks pass: clear for payment review.

The workflow never says "reject". The same time-bar defence has also failed in court, so that call belongs to a person.

## Slide 6 — Reliability (3:35–4:35)

Three design choices make this reliable.

One. When a value is covered or blurred, the workflow does not fill it in. It says "review needed" and tells the handler where to look.

Two. When the contract is silent, it does not assume. If the pumping log is unsigned but a protest is attached, the BPVOY4 clause does not say the protest is enough. So the case goes to a person.

Three. The model does no arithmetic. The deadline date is read from the charterer's own receipt record and compared with the date received.

I tested this with ten claim packages, fifty-one documents, built to break the workflow. And I separated the maker from the checker. Upstage Studio reads and decides. Claude built the test documents and scored the runs. The answer key comes from rule code, not from either model.

## Slide 7 — Results (4:35–5:10)

Here is what happened when I ran it.

On the first full run, nine of ten decisions were right. The one failure was the late claim. The workflow said "review needed" instead of "time-bar risk", because the extraction marked a clean but very dense pumping log as unreadable. I removed that flag from the pumping log and kept it only for covered or smudged boxes on the statement of facts.

After that fix, all ten decisions matched the answer key, and they matched again when I ran the final set twice from start to finish.

Then I built thirteen packages the workflow had never seen: two documents missing at once, a late claim with a missing log, pages in reverse order. Thirty-three runs, thirty-three correct decisions.

Those new cases also showed me one weakness. With no invoice in the bundle, the workflow invented a placeholder for the vessel name. The decision was still right, and I list it as an open issue. Each claim package takes about half a minute.

## Slide 8 — Service (5:10–5:45)

The output is not only a label. For each decision, the handler gets the next document.

If documents are missing, a draft letter to the owners, in English, listing exactly what is missing and the deadline. If there is a time-bar risk or a mismatch, a short memo with the two dates or the two values. If the claim is clear, a memo of what was confirmed, so the handler goes straight to the calculation.

On the screen you see a real run: the pumping log with an empty terminal signature line on the left, and the draft letter on the right.

## Slide 9 — Close (5:45–6:00)

To sum up: one missing signature can erase a claim. TimeBar checks the evidence in one pass, hands over when it is not sure, and prepares the next step.

Thank you. I'm happy to take your questions.

---

## Q&A — 준비할 답 (초안)

**Q. Isn't this a shipping problem, not an energy problem?**
The documents are produced at the terminal during cargo operations: the notice of readiness, the statement of facts, the pumping log. Bahri's accounts show the Aramco group as its largest customer, and say the charterer pays for delay. The amounts Aramco paid are not disclosed, so that link is my inference, and I say so rather than guess.

**Q. Why not calculate the demurrage amount too?**
In the cases I showed, the claims were not lost on the amount. They were lost on missing documents and deadlines. I chose the part where a mistake costs the whole claim, and where the answer can be checked against a clear rule.

**Q. Charter parties differ. Does this only work for BPVOY4?**
Yes, the rules in this version follow BPVOY4, clause 20.1. The structure is the same for other forms: a deadline, a list of documents, signatures. Changing the form means changing the criteria in one Instruct node and the receipt record, not the whole workflow.

**Q. How do you know the model reads a signature correctly?**
I test it directly: two cases have an empty terminal signature line, and the extraction returned "not signed" for both in every run. If a value cannot be read, the case goes to review.

**Q. Why is the deadline date on a document instead of being calculated?**
A language model can miscount days. A claims register already records the date received and the deadline. Reading two dates and comparing them is more reliable than asking the model to add ninety days.

**Q. Four of your ten cases end in "review needed". Is that automation?**
Those four are the hard cases on purpose. Even then the handler gets the reason and the place to look. The other six are sorted without anyone opening six documents.

**Q. How did you use AI tools in building this?**
I set the criteria and made the decisions. Claude collected sources, built the test documents and scored the runs. Upstage Studio does the reading and judging. I checked Claude's claims against the original judgments, and several of its first claims were wrong, so I corrected them.

**Q. What would you do next?**
Ask a real claims team which document problem is most common, and add the charter party recap as a seventh document so special terms can be checked.
