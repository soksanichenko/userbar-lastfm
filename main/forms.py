from __future__ import annotations

import logging

import wtforms.validators as validators
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.widgets import Input

from config import LASTFM_API_KEY
from utils.api import LastFmException, User

logger = logging.getLogger(__name__)


def username_validate(form: FlaskForm, field: StringField) -> None:
    """Validate that the Last.fm username exists and has recent tracks."""
    logger.debug('validating username: %s', field.data)
    user = User(LASTFM_API_KEY, username=field.data)
    try:
        user.user_get_recent_tracks(extended=1)
    except LastFmException as error:
        field.errors.append(error.message)
        raise validators.StopValidation()


class Generator(FlaskForm):
    username = StringField('Username', validators=[username_validate], default='ZelGray')
    inner_color = StringField('Inner color', validators=[validators.DataRequired()],
                              widget=Input(input_type='color'), default='#000000')
    outer_color = StringField('Outer color', validators=[validators.DataRequired()],
                              widget=Input(input_type='color'), default='#FFFFFF')
    text_color = StringField('Text color', validators=[validators.DataRequired()],
                             widget=Input(input_type='color'), default='#FFFFFF')
    border_color = StringField('Border color', widget=Input(input_type='color'), default='#000000')
    enable_border = BooleanField('Enable border', default=False)
    logo_color = StringField('Logo color', widget=Input(input_type='color'), default='#000000')
    enable_logo = BooleanField('Enable logo', default=False)
    truncate_text = BooleanField('Truncate image (to 750px)', default=False)
