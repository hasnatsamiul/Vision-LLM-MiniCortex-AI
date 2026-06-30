# LEAD_NOTES.md

## Section A - Team Task Breakdown

As the Tech Lead, I would split the work so that each person owns a clear part of the pipeline, but we still review the full flow together.

I would take ownership of the overall architecture, final integration, and the Groq LLM connection. I would handle this part because API calls, response parsing, `.env` configuration, and fallback behavior are the riskiest parts of the project. I would also make sure the final output from Task 1 connects smoothly with the insight layer in Task 2.

Junior Intern 1 would work on the Task 1 inspection service. Their responsibility would be image path validation, supported format checks, processing time calculation, and returning the structured JSON response. This is a good task because it is core Python logic and gives them a clear, testable responsibility.

Junior Intern 2 would work on Task 2 support work, especially the prompt file, fallback message, and unit tests with mocked LLM responses. This gives them hands-on experience with LLM-based features while keeping the work safe and easy to verify without depending on real API calls.

For the daily standup, I would keep it short and practical. Each person would share what they finished, what they plan to do next, and where they are blocked. I would also quickly check whether the Task 1 JSON format has changed, because Task 2 depends directly on that structure.

## Section B - Risk Log

Risk 1: The LLM may give inconsistent or wrong defect results in a real factory environment.  
Mitigation: I would add strict output validation, confidence thresholds, and a manual QA review step for uncertain or high-risk cases.

Risk 2: The external API may be slow or unavailable during production inspection.  
Mitigation: I would add timeout handling, retries, queue-based processing, and a fallback local inspection method so the factory process does not fully stop.

Risk 3: Image quality may be poor because of bad lighting, camera movement, blur, or wrong camera position.  
Mitigation: I would add a basic image quality check before inspection and ask for recapture when the image is too dark, blurry, or low quality.

## Section C - What You Would Improve

If I had two extra days, I would first improve validation, logging, and traceability. I would add a strict schema for the LLM output so the system can reject incomplete or unexpected responses before they affect the final result.

I would also add structured logs for the image filename, defect status, confidence score, processing time, and error type. This would make the system easier to debug and more trustworthy in production, because the team could understand why a part was flagged and what happened during inspection.