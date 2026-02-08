from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    DecimalField,
    IntegerField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Optional,
    NumberRange,
)


class RegisterForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6, max=128)],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    company_name = StringField(
        "Company Name",
        validators=[DataRequired(), Length(max=150)],
    )
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class ProfileForm(FlaskForm):
    company_name = StringField(
        "Company Name",
        validators=[DataRequired(), Length(max=150)],
    )
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])
    website = StringField("Website", validators=[Optional(), Length(max=255)])
    location = StringField("Location", validators=[Optional(), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(max=50)])
    contact_email = StringField(
        "Contact Email",
        validators=[Optional(), Email(), Length(max=120)],
    )
    submit = SubmitField("Save Profile")


class ServiceForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    category = StringField("Category", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = DecimalField(
        "Price (USD)",
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
    )
    delivery_time = IntegerField(
        "Delivery Time (days)",
        validators=[DataRequired(), NumberRange(min=1, max=365)],
    )
    tags = StringField("Tags (comma-separated)", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Save Service")


class MessageForm(FlaskForm):
    content = TextAreaField(
        "Message",
        validators=[DataRequired(), Length(min=1, max=2000)],
    )
    submit = SubmitField("Send Message")


class OrderStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("completed", "Completed"),
            ("rejected", "Rejected"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update Status")
