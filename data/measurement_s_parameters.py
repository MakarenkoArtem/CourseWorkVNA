import sqlalchemy
from .db_session import SqlAlchemyBase


class MeasurementSParameter(SqlAlchemyBase):
    __tablename__ = "measurement_s_parameters"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    measurement_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("measurement_data.id")
    )
    s_parameter = sqlalchemy.Column(sqlalchemy.String(4))  # s11, s12, s21, s22
    frequency_point_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("measurement_frequency_points.id")
    )
    real_part = sqlalchemy.Column(sqlalchemy.Float)
    imaginary_part = sqlalchemy.Column(sqlalchemy.Float)
