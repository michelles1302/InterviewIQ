import re
from typing import Dict, Any, List

# Cues per structural component
FRAMEWORK_CUES = {
    "behavioral": {
        "Situation": [
            r'\bwhen I\b', r'\bat my previous\b', r'\bduring my time\b', r'\bthe project was\b',
            r'\bour team was\b', r'\bthe company\b', r'\bbackground\b', r'\bcontext\b', r'\bwe faced\b'
        ],
        "Task": [
            r'\bmy role\b', r'\bmy task\b', r'\bmy responsibility\b', r'\bI was assigned\b',
            r'\bI was tasked\b', r'\bthe goal was\b', r'\bI needed to\b', r'\bobjective\b'
        ],
        "Action": [
            r'\bI created\b', r'\bI built\b', r'\bI implemented\b', r'\bI designed\b',
            r'\bI analyzed\b', r'\bI organized\b', r'\bI communicated\b', r'\bI decided\b',
            r'\bI refactored\b', r'\bI led\b', r'\bI took initiative\b', r'\bI developed\b'
        ],
        "Result": [
            r'\bas a result\b', r'\bconsequently\b', r'\bthe outcome\b', r'\bresulted in\b',
            r'\bincreased\b', r'\breduced\b', r'\bsaved\b', r'\bachieved\b', r'\bimproved by\b',
            r'\bfinally\b', r'\bimpact\b', r'\bdelivered\b', r'\bsuccessfully\b'
        ]
    },
    "technical": {
        "Definition": [
            r'\bis defined as\b', r'\brefers to\b', r'\bis a concept\b', r'\bis a mechanism\b',
            r'\bmeans that\b', r'\bis used to\b', r'\bstands for\b', r'\bis an approach\b'
        ],
        "Explanation": [
            r'\bworks by\b', r'\bunder the hood\b', r'\bbecause\b', r'\bdue to\b',
            r'\bin order to\b', r'\bhow it operates\b', r'\bthe core mechanism\b', r'\bprocess involves\b'
        ],
        "Example": [
            r'\bfor example\b', r'\bsuch as\b', r'\bfor instance\b', r'\bconsider a scenario\b',
            r'\be\.g\.\b', r'\blike when\b', r'\ban example of this\b'
        ],
        "Application": [
            r'\bbest used when\b', r'\bin practice\b', r'\bin production\b', r'\buse case\b',
            r'\bwhen building\b', r'\bwhen designing\b', r'\btrade-off\b', r'\bapplication\b'
        ]
    },
    "project": {
        "Problem": [r'\bproblem\b', r'\bchallenge\b', r'\bissue\b', r'\bneed\b', r'\bgoal\b'],
        "Approach": [r'\bapproach\b', r'\bstrategy\b', r'\bdesigned\b', r'\barchitecture\b', r'\bplanned\b'],
        "Technology": [r'\busing\b', r'\bstack\b', r'\btechnologies\b', r'\bbuilt with\b', r'\bframework\b', r'\bdatabase\b'],
        "Result": [r'\bresult\b', r'\bimpact\b', r'\boutcome\b', r'\bperformance\b', r'\bdeployed\b', r'\bmetrics\b']
    },
    "hr": {
        "Core Position": [r'\bI believe\b', r'\bmy goal\b', r'\bmy passion\b', r'\bI am drawn to\b', r'\bmy perspective\b'],
        "Reasoning/Context": [r'\bbecause\b', r'\bmy experience in\b', r'\bthroughout my career\b', r'\baligns with\b'],
        "Value/Impact": [r'\bI can bring\b', r'\bmy value\b', r'\bcontribute to\b', r'\bhelp the team\b', r'\bdrive success\b']
    }
}


def analyze_structure(answer: str, structure_type: str = "technical") -> Dict[str, Any]:
    """
    Analyzes logical structure of the answer against defined structural frameworks (e.g. STAR).
    """
    if not answer.strip():
        return {
            "score": 0.0,
            "found_elements": {},
            "missing_elements": [],
            "framework_used": structure_type,
            "feedback": "No answer provided to analyze structure."
        }

    # Normalize structure_type
    st_key = structure_type.lower()
    if st_key not in FRAMEWORK_CUES:
        if "behavioral" in st_key or "leadership" in st_key:
            st_key = "behavioral"
        elif "project" in st_key:
            st_key = "project"
        elif "hr" in st_key:
            st_key = "hr"
        else:
            st_key = "technical"

    cues_dict = FRAMEWORK_CUES[st_key]
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer) if s.strip()]
    answer_lower = answer.lower()

    found_elements = {}
    missing_elements = []

    for element_name, pattern_list in cues_dict.items():
        found = False
        matching_sentence = ""
        
        for pat in pattern_list:
            match = re.search(pat, answer_lower)
            if match:
                found = True
                # Find matching sentence snippet
                for sent in sentences:
                    if re.search(pat, sent.lower()):
                        matching_sentence = sent
                        break
                break
        
        if found:
            found_elements[element_name] = matching_sentence if matching_sentence else "Detected"
        else:
            missing_elements.append(element_name)

    total_elements = len(cues_dict)
    found_count = len(found_elements)

    # Base score calculated from percentage of structural elements present
    if total_elements > 0:
        base_score = (found_count / total_elements) * 100.0
    else:
        base_score = 100.0

    # Paragraph or transition connector bonus (+ 10 points up to 100 if paragraphs/transitions exist)
    connectors = [r'\bfirstly\b', r'\bsecondly\b', r'\bfurthermore\b', r'\bhowever\b', r'\btherefore\b', r'\bin summary\b', r'\boverall\b']
    connector_found = any(re.search(c, answer_lower) for c in connectors)
    
    score = base_score
    if connector_found and score < 100:
        score += 10.0
    
    # Extra check for STAR: result is critical in behavioral
    if st_key == "behavioral" and "Result" in missing_elements:
        score = min(score, 75.0)

    score = round(float(max(0.0, min(100.0, score))), 1)

    # Generate feedback
    if len(missing_elements) == 0:
        feedback = f"Excellent structure! Your answer contains all key components of the {st_key.upper()} framework."
    else:
        missing_str = ", ".join(missing_elements)
        if st_key == "behavioral":
            feedback = f"Your answer is missing key elements of the STAR framework: {missing_str}. Make sure to include concrete Actions and measurable Results."
        elif st_key == "technical":
            feedback = f"Your technical explanation would be stronger by explicitly adding: {missing_str}."
        else:
            feedback = f"Your answer structure is missing: {missing_str}."

    return {
        "score": score,
        "found_elements": found_elements,
        "missing_elements": missing_elements,
        "framework_used": st_key.upper(),
        "feedback": feedback
    }
