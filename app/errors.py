"""Helpers for user-facing validation errors."""


class FormError(Exception):
    def __init__(self, errors):
        super().__init__("Form validation failed")
        self.errors = errors


def field_error(errors, field, message):
    errors.setdefault(field, []).append(message)
