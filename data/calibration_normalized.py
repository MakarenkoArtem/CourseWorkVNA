import sqlalchemy
from .db_session import SqlAlchemyBase


class CalibrationStandardNormalized(SqlAlchemyBase):
    __tablename__ = "calibration_standards_normalized"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    standard_type = sqlalchemy.Column(
        sqlalchemy.String, nullable=False
    )  # 'open', 'short', 'match', 'thru', '2match'
    port = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # 3 или 6
    measurement_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
