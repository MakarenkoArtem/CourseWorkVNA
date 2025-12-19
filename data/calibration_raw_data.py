import sqlalchemy
from .db_session import SqlAlchemyBase


class CalibrationRawData(SqlAlchemyBase):
    __tablename__ = "calibration_raw_data"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    calibration_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("calibration_standards_normalized.id")
    )
    frequency_point_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("calibration_frequency_points.id")
    )
    b0_3_real = sqlalchemy.Column(sqlalchemy.Float)
    b0_3_imag = sqlalchemy.Column(sqlalchemy.Float)
    a0_real = sqlalchemy.Column(sqlalchemy.Float)
    a0_imag = sqlalchemy.Column(sqlalchemy.Float)
    b3_3_real = sqlalchemy.Column(sqlalchemy.Float)
    b3_3_imag = sqlalchemy.Column(sqlalchemy.Float)
    b0_6_real = sqlalchemy.Column(sqlalchemy.Float)
    b0_6_imag = sqlalchemy.Column(sqlalchemy.Float)
    a3_real = sqlalchemy.Column(sqlalchemy.Float)
    a3_imag = sqlalchemy.Column(sqlalchemy.Float)
    b3_6_real = sqlalchemy.Column(sqlalchemy.Float)
    b3_6_imag = sqlalchemy.Column(sqlalchemy.Float)
