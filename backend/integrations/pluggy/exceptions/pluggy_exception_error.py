from integrations.pluggy.schemas.base_error_schema import BaseErrorSchema


class PluggyExceptionError(Exception):
    def __init__(self, error: BaseErrorSchema):
        self.error = error
        super().__init__(f"{error.code} {error.code_description}: {error.message}")
