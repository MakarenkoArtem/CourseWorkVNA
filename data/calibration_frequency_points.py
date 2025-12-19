import sqlalchemy
from .db_session import SqlAlchemyBase


class CalibrationFrequencyPoint(SqlAlchemyBase):
    __tablename__ = "calibration_frequency_points"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    calibration_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("calibration_standards_normalized.id")
    )
    frequency_mhz = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
