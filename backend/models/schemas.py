# from dataclasses import dataclass, asdict
# from typing import Optional

# @dataclass
# class ExtractedDocumentData:
#     name: Optional[str] = None
#     passport_number: Optional[str] = None
#     dob: Optional[str] = None
#     expiry: Optional[str] = None
#     nationality: Optional[str] = None

#     def to_dict(self):
#         return asdict(self)

# @dataclass
# class VerificationChecks:
#     mrz_match: bool = False
#     database_match: bool = False
#     face_match: bool = False

# @dataclass
# class ForensicsResults:
#     metadata_suspicious: bool = False
#     ela_suspicious: bool = False
#     image_inconsistency: bool = False

# @dataclass
# class PipelineResult:
#     document: ExtractedDocumentData
#     verification: VerificationChecks
#     forensics: ForensicsResults
#     verification_score: int = 0
#     decision: str = "PENDING"