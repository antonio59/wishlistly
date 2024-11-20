from enum import Enum

class PriorityLevel(str, Enum):
    MUST_HAVE = "Must Have"
    WOULD_LIKE = "Would Like"
    NICE_TO_HAVE = "Nice to Have"
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.value) for choice in cls]
    
    def __str__(self):
        return self.value

class FeedbackType(str, Enum):
    BUG = "Bug Report"
    FEATURE = "Feature Request"
    GENERAL = "General Feedback"
    SUPPORT = "Support Request"
    OTHER = "Other"
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.value) for choice in cls]
    
    def __str__(self):
        return self.value
