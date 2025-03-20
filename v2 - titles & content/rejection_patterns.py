import re


class RejectionPattern:
    """
    Detector for identifying referendums that request 'nay' votes based on text patterns.

    This class analyzes referendum titles and content for specific patterns
    indicating that the referendum should be rejected or voted against.
    """

    def __init__(self):
        """
        Initialize detector with pattern lists for identifying 'nay' vote requests.

        Sets up pattern categories with varying confidence levels:
        - strong_patterns: High confidence indicators (0.95)
        - medium_patterns: Medium confidence indicators (0.85)
        - weak_patterns: Low confidence indicators
        - content_patterns: Patterns specific to content text
        - negative_patterns: Patterns that override positive matches
        """
        self.strong_patterns = [
            r'(?i)reject\s+this\s+(referendum|proposal|motion)',         # reject this proposal/referendum/motion
            r'(?i)please\s+reject\s+(this|the)',                         # please reject this or please reject the
            r'(?i)reject\s+.*referendum\s+#?\d+',                        # reject referendum
            r'(?i)reject\s+.*proposal\s+#?\d+',                          # reject proposal
            r'(?i)\bvote\s+nay\b',                                       # vote nay
            r'(?i)please\s+vote\s+nay\b',                                # please vote nay
            r'(?i)\bvote\s+no\b',                                        # vote no
            r'(?i)do\s+not\s+vote\s+(for|on)',                           # do not vote for/on
            r'(?i)don\'t\s+vote\s+(for|on)',                             # don't vote for/on
            r'(?i)please\s+ignore\s+this',                               # please ignore this
            r'(?i)ignore\s+this\s+(referendum|proposal)',                # ignore this referendum/proposal
            r'(?i)created\s+in\s+error',                                 # created in error
            r'(?i)wrong\s+(preimage|submission|parameter|pre-image)',    # Wrong parameters/submission
            r'(?i)mistake\s+in\s+preimage',                              # mistake in preimage
            r'(?i)\bunnote\b',                                           # unnote
            r'(?i)\bdo\s+not\s+place\s+decision\s+deposit\b',            # Specific governance instruction
            r'(?i)\b(please|do)\s+vote\s+(nay|no|against)\s+this\b',     # please vote nay/no/against this
            r'(?i)\ballow\s+it\s+(to\s+)?timeout\b',                     # allow it to timeout
            r'(?i)^\s*reject\s*$',                                       # Just the word "reject" alone
            r'(?i)^\s*(\.|-){1,3}\s*$',                                  # Placeholder titles with dots or dashes
            r'(?i)\[nay this proposal\]',                                # [nay this proposal]
            r'(?i)\bnay this proposal\b',                                # nay this proposal
            r'(?i)vote\s+nay\s*[-\s]*',                                  # vote nay -
            r'(?i)change\s+your\s+vote\s+to\s+nay',                      # change your vote to nay
            r'(?i)ignore\s*\/?\s*nay',                                   # ignore/nay
            r'(?i)\bduplicate\s+ref(erendum)?\b',                        # duplicate referendum" or duplicate ref
            r'(?i)vote\s+for\s+nay\b',                                   # vote for nay
            r'(?i)test\s+.*\s+vote\s+(for|)\s*nay',                      # Test proposals
            r'(?i)\[vote\s+nay\b',                                       # [vote nay
            r'(?i)resubmission\s+in\s+process',                          # resubmission in process
            r'(?i)will\s+be\s+sent\s+again',                             # will be sent again
        ]

        self.medium_patterns = [
            r'(?i)preimage\s+(removed|pulled)',                          # Preimage was removed or pulled
            r'(?i)(incorrect|wrong)\s+(preimage|hash)',                  # Incorrect or wrong preimage/hash used
            r'(?i)vote\s+on\s+#\d+\s+instead',                           # Directing to vote on a different referendum instead
            r'(?i)\bcancelled\b',                                        # Simple "cancelled" with word boundaries
            r'(?i)\[cancelled\]',                                        # "[cancelled]" format used in titles
            r'(?i)cancelling\s+this\s+one',                              # "cancelling this one" phrase
            r'(?i)posted\s+on\s+wrong\s+track',                          # Wrong governance track used
            r'(?i)wrong\s+track\b',                                      # Simple "wrong track" mention
            r'(?i)wrong\s+dot\s+amount',                                 # Incorrect DOT amount specified
            r'(?i)wrong\s+function',                                     # Wrong function used in the proposal
            r'(?i)wrong\s+category',                                     # Wrong category selected for the proposal
        ]

        self.weak_patterns = [
            r'(?i)\bplease\s+nay\b',                                     # please nay
            r'(?i)\berror\s+in\s+(submission|referendum|proposal)\b',    # Mentions an error but without explicit rejection request
            r'(?i)\bmistake\s+in\s+(submission|referendum|proposal)\b',  # Mentions a mistake but without explicit rejection instruction
        ]

        self.content_patterns = [
            r'(?i)please\s+reject\s+this',                               # please reject this
            r'(?i)reject\s+this\s+referendum',                           # reject this referendum
            r'(?i)Please reject this proposal',                          # Please reject this proposal
            r'(?i)\bvote\s+nay\s+on\s+this\b',                           # vote nay on this
            r'(?i)vote\s+against\s+this',                                # vote against this
            r'(?i)\bvote\s+no\s+on\s+this\b',                            # vote no on this
            r'(?i)bug\s*/\s*error\s+in\s+this',                          # bug/error in this
            r'(?i)will\s+resubmit\s+a\s+corrected',                      # will resubmit a corrected
            r'(?i)we\s+will\s+resubmit',                                 # we will resubmit
            r'(?i)will\s+resubmit\s+it',                                 # will resubmit it
            r'(?i)resubmit.*proposal',                                   # resubmit followed by proposal
            r'(?i)reject.*resubmit',                                     # reject followed by resubmit
        ]

        self.negative_patterns = [
            r'(?i)don\'t\s+miss',                                        # don't miss
            r'(?i)no\s+need\s+to\s+vote\s+nay',                          # Explicitly stating NOT to vote nay
            r'(?i)\.dot\b',                                              # References to .dot (file format) or DOT token
            r'(?i)\breplace.{0,10}(curator|bounty)',                     # Replace curator/bounty discussion
            r'(?i)(bond|deposit|spend).{0,20}(return|reimburs)',         # Financial returns or reimbursements
            r'(?i)reject.{0,20}(malicious|attack|spam)',                 # Rejecting attacks or malicious content
            r'(?i)reject.{0,20}(if|should).{0,20}(you|community)',       # Conditional rejection statements
            r'(?i)to\s+reject\s+invalid',                                # Rejecting invalid items, not the proposal itself
            r'(?i)ability\s+to\s+reject',                                # Discussing the ability to reject
            r'(?i)option\s+to\s+reject',                                 # Discussing rejection as an option
            r'(?i)power\s+to\s+reject',                                  # Discussing power to reject
            r'(?i)right\s+to\s+reject',                                  # Discussing right to reject
            r'(?i)(can|may|might|could|should|would)\s+reject',          # Hypothetical rejection discussions
            r'(?i)(polkadot|kusama|substrate)\s+reject',                 # Networks rejecting things
            r'(?i)reject\s+any\s+(invalid|malicious)',                   # Rejecting invalid entries
            r'(?i)(validators|nominators|collators)\s+reject',           # Validators rejecting something
            r'(?i)reject\s+unauthorized',                                # Rejecting unauthorized actions
            r'(?i)(treasury|council|fellowship)\s+reject',               # Governance bodies doing rejections
            r'(?i)governance\s+can\s+reject',                            # Governance mechanism discussions
            r'(?i)(refund|reimbursement|retroactive)(?!.*nay|.*vote|.*reject|.*change)',                                  # Payment terms but not with nay indicators
            r'(?i)(retry|resubmission|redux)(?!.*vote\s+nay|.*nay\s+this)',                                               # Resubmission but not with nay instructions
            r'(?i)(bond|deposit|spend|motion).{0,20}(reject|return)(?!.*vote\s+nay|.*change.*vote)',                      # Financial terms but not when nay voting mentioned
            r'(?i)(maintenance|development|proposal|funding|proposal).{0,20}(for|of)(?!.*nay|.*vote|.*reject|.*change)',  # Purpose descriptions but not with nay requests
        ]

    def check_text(self, text, is_content=False):
        """
        Checks text for patterns indicating a rejection or negative vote.

        Analyzes text against multiple pattern categories (override, negative, strong, medium,
        content-specific, and keyword patterns) with varying confidence levels.

        Args:
            text (str): Text to analyze
            is_content (bool): If True, applies additional content-specific patterns

        Returns:
            tuple: (is_match, confidence, explanation)
                - is_match (bool): Whether text matches rejection criteria
                - confidence (float): Score from 0.0-0.95 indicating match strength
                - explanation (str): Description of which pattern matched or why no match

        Pattern priority:  Override patterns
                          -> Negative patterns
                          -> Empty/placeholder check
                          -> Strong patterns
                          -> Medium patterns
                          -> Content patterns
                          -> Contextual keywords
                          -> Simple keywords
        """
        if not text or not isinstance(text, str):
            return False, 0.0, "Empty or invalid text"

        override_patterns = [
            (r'(?i)vote\s*nay', 0.95, "Contains 'vote nay'"),
            (r'(?i)change.*vote.*nay', 0.95, "Contains vote change instruction"),
            (r'(?i)\bNAY\b', 0.95, "Contains capitalized NAY")
        ]

        for pattern, confidence, explanation in override_patterns:
            if re.search(pattern, text):
                return True, confidence, explanation

        for pattern in self.negative_patterns:
            if re.search(pattern, text):
                return False, 0.0, f"Negative pattern matched: {pattern}"

        # Check if this is just a placeholder (single char or dash)
        is_empty_title = bool(re.match(r'^\s*[.-]{1,3}\s*$', text))
        if is_empty_title:
            return True, 0.95, f"Empty/placeholder referendum: '{text}'"

        for pattern in self.strong_patterns:
            match = re.search(pattern, text)
            if match:
                return True, 0.95, f"Strong indicator: '{match.group(0)}'"

        for pattern in self.medium_patterns:
            match = re.search(pattern, text)
            if match:
                return True, 0.85, f"Medium indicator: '{match.group(0)}'"

        if is_content:
            for pattern in self.content_patterns:
                match = re.search(pattern, text)
                if match:
                    return True, 0.9, f"Content indicator: '{match.group(0)}'"

        keywords_with_context = [
            (r'\bnay\b', r'vote\s+nay|please\s+nay'),
            (r'\breject\b', r'reject\s+this|please\s+reject'),
            (r'\berror\b', r'error\s+in|due\s+to\s+error'),
            (r'\bwrong\b', r'wrong\s+\w+|is\s+wrong'),
            (r'\bmistake\b', r'mistake\s+in|by\s+mistake'),
            (r'\bincorrect\b', r'incorrect\s+\w+|is\s+incorrect'),
            (r'\bcancel\b', r'cancel\s+this|please\s+cancel'),
            (r'\bignore\b', r'ignore\s+this|please\s+ignore'),
            (r'\bagainst\b', r'vote\s+against')
        ]

        matches = []

        for keyword, context in keywords_with_context:
            if re.search(keyword, text.lower()) and re.search(context, text.lower()):
                matches.append(keyword.strip(r'\b'))

        if len(matches) >= 2:
            return True, 0.7, f"Multiple weak indicators with context: {', '.join(matches)}"
        elif len(matches) == 1:
            return True, 0.6, f"Weak indicator with context: '{matches[0]}'"

        simple_keywords = ["nay", "reject", "error", "wrong", "mistake"]
        simple_matches = [k for k in simple_keywords if re.search(rf'\b{k}\b', text.lower())]

        if len(simple_matches) >= 2:
            return True, 0.55, f"Multiple weak indicators without context: {', '.join(simple_matches)}"

        return False, 0.0, "No pattern matched"

    def detect(self, title, content=""):
        """
        Detects if a referendum requests a 'nay' vote.

        Evaluates title and content text through multiple detection methods,
        prioritizing direct matches (NAY keyword, vote instructions) before
        using pattern matching via check_text().

        Args:
            title (str): Referendum title
            content (str, optional): Additional referendum text

        Returns:
            dict: Detection results containing:
                - is_nay_request (bool): Whether text indicates a nay vote request
                - confidence (float): Score from 0.0-0.95 indicating detection confidence
                - explanation (str): Description of detection reasoning
        """
        title = title.strip() if title else ""
        content = content.strip() if content else ""

        if "NAY" in title or "NAY" in content:
            return {
                "is_nay_request": True,
                "confidence": 0.95,
                "explanation": f"Contains capitalized 'NAY'"
            }

        vote_nay_pattern = r'(?i)vote\s*nay'
        change_vote_pattern = r'(?i)change.*vote.*nay'
        if re.search(vote_nay_pattern, title) or re.search(change_vote_pattern, title):
            return {
                "is_nay_request": True,
                "confidence": 0.95,
                "explanation": f"Title contains direct vote nay instruction"
            }

        if "cancelled" in title.lower() or "[cancelled]" in title.lower():
            return {
                "is_nay_request": True,
                "confidence": 0.9,
                "explanation": f"Cancelled proposal: '{title}'"
            }

        title_is_nay, title_confidence, title_explanation = self.check_text(title)

        if title_is_nay and title_confidence >= 0.85:
            return {
                "is_nay_request": True,
                "confidence": title_confidence,
                "explanation": title_explanation
            }

        # Check content if provided
        content_is_nay, content_confidence, content_explanation = False, 0.0, ""
        if content:
            content_is_nay, content_confidence, content_explanation = self.check_text(content, is_content=True)

        if content_is_nay and content_confidence >= 0.7:
            return {
                "is_nay_request": True,
                "confidence": content_confidence,
                "explanation": content_explanation
            }

        if title_is_nay and content_is_nay:
            combined_confidence = max(title_confidence, content_confidence) + 0.1
            return {
                "is_nay_request": True,
                "confidence": min(combined_confidence, 0.9),
                "explanation": f"Combined evidence: {title_explanation}; {content_explanation}"
            }

        if title_is_nay:
            return {
                "is_nay_request": True,
                "confidence": title_confidence,
                "explanation": title_explanation
            }

        return {
            "is_nay_request": False,
            "confidence": 0.9,
            "explanation": "No indicators of a 'nay' vote request found"
        }
