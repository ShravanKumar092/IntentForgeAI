class ProjectNotFoundError(RuntimeError):
    pass


class ProjectIntentNotFoundError(RuntimeError):
    pass


class RequirementNotFoundError(RuntimeError):
    pass


class SourceNotFoundError(RuntimeError):
    pass


class DuplicateSourceError(RuntimeError):
    pass


class EvidenceNotFoundError(RuntimeError):
    pass


class DuplicateEvidenceRelationshipError(RuntimeError):
    pass
