from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from flask import current_app

class ForgotPasswordSchema(Schema):
    """
    Schema for validating forgot password request payload.
    """
    email = fields.Email(
        required=True, 
        error_messages={"required": "Email is required.", "invalid": "Invalid email format."}
    )

class LoginSchema(Schema):
    """
    Schema for validating login request payload.
    """
    userId = fields.Email(required=True, error_messages={"required": "User ID is required.", "invalid": "Invalid email format."})
    # password = fields.Str(required=True, validate=lambda p: len(p) > 0, error_messages={"required": "Password is required."})
    password = fields.Str(required=True, error_messages={"required": "Password is required."})

    @validates("password")
    def validate_password(self, password):
        """
        Ensures password is not empty and meets any additional criteria (optional).
        """
        if len(password.strip()) == 0:
            raise ValidationError("Password cannot be empty.")
