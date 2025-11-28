import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Setting(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'settings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    freq_start_mhz = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    freq_stop_mhz = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    num_freq_points = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    rbw_khz = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    output_power_dbm = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    txtr = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    mode = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

