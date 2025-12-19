import sqlalchemy
from .db_session import SqlAlchemyBase


class MeasurementFrequencyPoint(SqlAlchemyBase):
    __tablename__ = "measurement_frequency_points"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    measurement_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("measurement_data.id")
    )
    frequency_mhz = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
