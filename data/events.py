import sqlalchemy
from werkzeug.security import check_password_hash, generate_password_hash
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Event(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_settings = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
