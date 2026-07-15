# LEAD_NOTES.md


## Section A - Risk Log

Risk 1: The LLM may give inconsistent or wrong defect results in a real factory environment.  
Mitigation: I would add strict output validation, confidence thresholds, and a manual QA review step for uncertain or high-risk cases.

Risk 2: The external API may be slow or unavailable during production inspection.  
Mitigation: I would add timeout handling, retries, queue-based processing, and a fallback local inspection method so the factory process does not fully stop.

Risk 3: Image quality may be poor because of bad lighting, camera movement, blur, or wrong camera position.  
Mitigation: I would add a basic image quality check before inspection and ask for recapture when the image is too dark, blurry, or low quality.

## Section B - Improvement

For future improvement, the system could be enhanced with stronger validation, structured logging, better error handling, and more comprehensive testing. It could also be trained and evaluated on a larger and more diverse image dataset to improve accuracy and reliability. Additional features such as real-time monitoring, explainable results, user feedback, and automated model updates could make the system more robust and suitable for production use.
