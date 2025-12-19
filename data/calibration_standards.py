import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
import json
from typing import List


class CalibrationStandard(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "calibration_standards"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    standard_type = sqlalchemy.Column(
        sqlalchemy.String, nullable=False
    )  # 'open', 'short', 'match', 'thru', '2match'
    port = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # 3 или 6
    measurement_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    frequency_data = sqlalchemy.Column(sqlalchemy.Text, nullable=False)  # JSON string
    raw_data = sqlalchemy.Column(sqlalchemy.Text, nullable=False)  # JSON string
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    def set_frequency_data(self, data: List[float]):
        """Установить данные частот"""
        self.frequency_data = json.dumps(data)

    def get_frequency_data(self) -> List[float]:
        """Получить данные частот"""
        return json.loads(self.frequency_data) if self.frequency_data else []

    def set_raw_data(self, data: List[List[float]]):
        """Установить сырые данные калибровочного стандарта"""
        # data - список списков [freq, b0_3_real, b0_3_imag, a0_real, a0_imag, b3_3_real, b3_3_imag, b0_6_real, b0_6_imag, a3_real, a3_imag, b3_6_real, b3_6_imag]
        self.raw_data = json.dumps(data)

    def get_raw_data(self) -> List[List[float]]:
        """Получить сырые данные калибровочного стандарта"""
        return json.loads(self.raw_data) if self.raw_data else []

    def to_dict(self):
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "author_id": self.author_id,
            "standard_type": self.standard_type,
            "port": self.port,
            "measurement_name": self.measurement_name,
            "frequency_data": self.get_frequency_data(),
            "raw_data": self.get_raw_data(),
            "created_at": self.created_at,
        }

    @staticmethod
    def create_standard(
        db_session,
        author_id,
        standard_type,
        port,
        measurement_name,
        frequency_data,
        raw_data,
    ):
        """Создать новую запись калибровочного стандарта"""
        standard = CalibrationStandard(
            author_id=author_id,
            standard_type=standard_type,
            port=port,
            measurement_name=measurement_name,
            created_at=datetime.now(),
        )
        standard.set_frequency_data(frequency_data)
        standard.set_raw_data(raw_data)
        db_session.add(standard)
        db_session.commit()
        return standard

    @staticmethod
    def get_standards_by_author(db_session, author_id, standard_type=None):
        """Получить все калибровочные стандарты для пользователя"""
        query = db_session.query(CalibrationStandard).filter(
            CalibrationStandard.author_id == author_id
        )
        if standard_type:
            query = query.filter(CalibrationStandard.standard_type == standard_type)
        return query.all()
