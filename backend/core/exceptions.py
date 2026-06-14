class NyayaSetuBaseError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


class EmailAlreadyExistsError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Email already registered", "EMAIL_ALREADY_EXISTS")


class InvalidCredentialsError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Invalid email or password", "INVALID_CREDENTIALS")


class AccountNotVerifiedError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Email not verified", "ACCOUNT_NOT_VERIFIED")


class InvalidTokenError(NyayaSetuBaseError):
    def __init__(self, detail: str = ""):
        super().__init__(f"Invalid or expired token: {detail}", "INVALID_TOKEN")


class FreeTierExhaustedError(NyayaSetuBaseError):
    def __init__(self, reset_at: str):
        super().__init__("Free tier exhausted", "FREE_TIER_EXHAUSTED")
        self.reset_at = reset_at


class QueryNotFoundError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Query not found", "QUERY_NOT_FOUND")


class AccessDeniedError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Access denied to this resource", "ACCESS_DENIED")


class PaymentRequiredError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Payment required", "PAYMENT_REQUIRED")


class PaymentVerificationError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Payment signature verification failed", "INVALID_SIGNATURE")


class PaymentAlreadyVerifiedError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Payment already processed", "PAYMENT_ALREADY_VERIFIED")


class PipelineError(NyayaSetuBaseError):
    def __init__(self, detail: str):
        super().__init__(f"Pipeline error: {detail}", "PIPELINE_ERROR")


class InsufficientPermissionsError(NyayaSetuBaseError):
    def __init__(self):
        super().__init__("Insufficient permissions", "INSUFFICIENT_PERMISSIONS")
