import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from typing import List, Tuple
import numpy as np
from datetime import datetime

from .measurement_frequency_points import MeasurementFrequencyPoint
from .measurement_raw_data import MeasurementRawData
from .measurement_s_parameters import MeasurementSParameter


class MeasurementData(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "measurement_data"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    measurement_type = sqlalchemy.Column(
        sqlalchemy.String, nullable=False
    )  # 'raw', 'calibrated', 'calibration_standard'
    measurement_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    @staticmethod
    def create_raw_measurement(
        db_session, author_id, measurement_name, frequency_data, raw_data
    ):
        """Создать новую запись сырых измерений"""
        measurement = MeasurementData(
            author_id=author_id,
            measurement_type="raw",
            measurement_name=measurement_name,
            created_at=datetime.now(),
        )
        db_session.add(measurement)
        db_session.flush()  # Получаем ID измерения

        for i, freq in enumerate(frequency_data):
            freq_point = MeasurementFrequencyPoint(
                measurement_id=measurement.id, frequency_mhz=freq
            )
            db_session.add(freq_point)

        for i, data_row in enumerate(raw_data):
            freq_point = (
                db_session.query(MeasurementFrequencyPoint)
                .filter(
                    MeasurementFrequencyPoint.measurement_id == measurement.id,
                    MeasurementFrequencyPoint.frequency_mhz == frequency_data[i],
                )
                .first()
            )

            if freq_point:
                raw_record = MeasurementRawData(
                    measurement_id=measurement.id,
                    frequency_point_id=freq_point.id,
                    b0_3_real=data_row[1],
                    b0_3_imag=data_row[2],
                    a0_real=data_row[3],
                    a0_imag=data_row[4],
                    b3_3_real=data_row[5],
                    b3_3_imag=data_row[6],
                    b0_6_real=data_row[7],
                    b0_6_imag=data_row[8],
                    a3_real=data_row[9],
                    a3_imag=data_row[10],
                    b3_6_real=data_row[11],
                    b3_6_imag=data_row[12],
                )
                db_session.add(raw_record)

        db_session.commit()
        return measurement

    @staticmethod
    def create_calibrated_measurement(
        db_session,
        author_id,
        measurement_name,
        frequency_data,
        s11_data,
        s12_data,
        s21_data,
        s22_data,
    ):
        """Создать новую запись откалиброванных измерений"""
        measurement = MeasurementData(
            author_id=author_id,
            measurement_type="calibrated",
            measurement_name=measurement_name,
            created_at=datetime.now(),
        )
        db_session.add(measurement)
        db_session.flush()  # Получаем ID измерения

        for i, freq in enumerate(frequency_data):
            freq_point = MeasurementFrequencyPoint(
                measurement_id=measurement.id, frequency_mhz=freq
            )
            db_session.add(freq_point)

        s_params = [
            ("s11", s11_data),
            ("s12", s12_data),
            ("s21", s21_data),
            ("s22", s22_data),
        ]

        for param_name, param_data in s_params:
            if param_data:
                for i, complex_val in enumerate(param_data):
                    freq_point = (
                        db_session.query(MeasurementFrequencyPoint)
                        .filter(
                            MeasurementFrequencyPoint.measurement_id == measurement.id,
                            MeasurementFrequencyPoint.frequency_mhz
                            == frequency_data[i],
                        )
                        .first()
                    )

                    if freq_point:
                        s_param = MeasurementSParameter(
                            measurement_id=measurement.id,
                            s_parameter=param_name,
                            frequency_point_id=freq_point.id,
                            real_part=complex_val.real,
                            imaginary_part=complex_val.imag,
                        )
                        db_session.add(s_param)

        db_session.commit()
        return measurement

    @staticmethod
    def create_calibration_standard(
        db_session,
        author_id,
        standard_type,
        port,
        measurement_name,
        frequency_data,
        raw_data,
    ):
        """Создать новую запись калибровочного стандарта"""
        measurement = MeasurementData(
            author_id=author_id,
            measurement_type="calibration_standard",
            measurement_name=measurement_name,
            created_at=datetime.now(),
        )
        db_session.add(measurement)
        db_session.flush()  # Получаем ID измерения

        for i, freq in enumerate(frequency_data):
            freq_point = MeasurementFrequencyPoint(
                measurement_id=measurement.id, frequency_mhz=freq
            )
            db_session.add(freq_point)

        for i, data_row in enumerate(raw_data):
            freq_point = (
                db_session.query(MeasurementFrequencyPoint)
                .filter(
                    MeasurementFrequencyPoint.measurement_id == measurement.id,
                    MeasurementFrequencyPoint.frequency_mhz == frequency_data[i],
                )
                .first()
            )

            if freq_point:
                raw_record = MeasurementRawData(
                    measurement_id=measurement.id,
                    frequency_point_id=freq_point.id,
                    b0_3_real=data_row[1],
                    b0_3_imag=data_row[2],
                    a0_real=data_row[3],
                    a0_imag=data_row[4],
                    b3_3_real=data_row[5],
                    b3_3_imag=data_row[6],
                    b0_6_real=data_row[7],
                    b0_6_imag=data_row[8],
                    a3_real=data_row[9],
                    a3_imag=data_row[10],
                    b3_6_real=data_row[11],
                    b3_6_imag=data_row[12],
                )
                db_session.add(raw_record)

        db_session.commit()
        return measurement

    @staticmethod
    def get_measurements_by_author(db_session, author_id, measurement_type=None):
        """Получить все измерения для пользователя"""
        query = db_session.query(MeasurementData).filter(
            MeasurementData.author_id == author_id
        )
        if measurement_type:
            query = query.filter(MeasurementData.measurement_type == measurement_type)
        return query.all()

    @staticmethod
    def get_measurement_by_id(db_session, measurement_id, author_id=None):
        """Получить измерение по ID"""
        query = db_session.query(MeasurementData).filter(
            MeasurementData.id == measurement_id
        )
        if author_id:
            query = query.filter(MeasurementData.author_id == author_id)
        return query.first()

    @staticmethod
    def delete_measurement(db_session, measurement_id, author_id):
        """Удалить измерение"""
        measurement = MeasurementData.get_measurement_by_id(
            db_session, measurement_id, author_id
        )
        if measurement:
            db_session.delete(measurement)
            db_session.commit()
            return True
        return False

    @staticmethod
    def get_latest_measurement(db_session, author_id, measurement_type):
        """Получить последнее измерение указанного типа"""
        return (
            db_session.query(MeasurementData)
            .filter(
                MeasurementData.author_id == author_id,
                MeasurementData.measurement_type == measurement_type,
            )
            .order_by(MeasurementData.created_at.desc())
            .first()
        )

    @staticmethod
    def get_measurement_details(db_session, measurement_id):
        """Получить детали измерения с данными"""
        measurement = (
            db_session.query(MeasurementData)
            .filter(MeasurementData.id == measurement_id)
            .first()
        )

        if not measurement:
            return None

        freq_points = (
            db_session.query(MeasurementFrequencyPoint)
            .filter(MeasurementFrequencyPoint.measurement_id == measurement_id)
            .order_by(MeasurementFrequencyPoint.frequency_mhz)
            .all()
        )

        frequency_data = [fp.frequency_mhz for fp in freq_points]

        raw_data = []
        if measurement.measurement_type in ["raw", "calibration_standard"]:
            raw_records = (
                db_session.query(MeasurementRawData)
                .filter(MeasurementRawData.measurement_id == measurement_id)
                .order_by(MeasurementRawData.frequency_point_id)
                .all()
            )

            raw_data = [
                [
                    fp.frequency_mhz,
                    rr.b0_3_real,
                    rr.b0_3_imag,
                    rr.a0_real,
                    rr.a0_imag,
                    rr.b3_3_real,
                    rr.b3_3_imag,
                    rr.b0_6_real,
                    rr.b0_6_imag,
                    rr.a3_real,
                    rr.a3_imag,
                    rr.b3_6_real,
                    rr.b3_6_imag,
                ]
                for fp, rr in zip(freq_points, raw_records)
            ]

        # Получаем S-параметры
        s11_data = []
        s12_data = []
        s21_data = []
        s22_data = []

        if measurement.measurement_type == "calibrated":
            s11_records = (
                db_session.query(MeasurementSParameter)
                .filter(
                    MeasurementSParameter.measurement_id == measurement_id,
                    MeasurementSParameter.s_parameter == "s11",
                )
                .order_by(MeasurementSParameter.frequency_point_id)
                .all()
            )

            s12_records = (
                db_session.query(MeasurementSParameter)
                .filter(
                    MeasurementSParameter.measurement_id == measurement_id,
                    MeasurementSParameter.s_parameter == "s12",
                )
                .order_by(MeasurementSParameter.frequency_point_id)
                .all()
            )

            s21_records = (
                db_session.query(MeasurementSParameter)
                .filter(
                    MeasurementSParameter.measurement_id == measurement_id,
                    MeasurementSParameter.s_parameter == "s21",
                )
                .order_by(MeasurementSParameter.frequency_point_id)
                .all()
            )

            s22_records = (
                db_session.query(MeasurementSParameter)
                .filter(
                    MeasurementSParameter.measurement_id == measurement_id,
                    MeasurementSParameter.s_parameter == "s22",
                )
                .order_by(MeasurementSParameter.frequency_point_id)
                .all()
            )

            s11_data = [complex(sr.real_part, sr.imaginary_part) for sr in s11_records]
            s12_data = [complex(sr.real_part, sr.imaginary_part) for sr in s12_records]
            s21_data = [complex(sr.real_part, sr.imaginary_part) for sr in s21_records]
            s22_data = [complex(sr.real_part, sr.imaginary_part) for sr in s22_records]

        return {
            "id": measurement.id,
            "author_id": measurement.author_id,
            "measurement_type": measurement.measurement_type,
            "measurement_name": measurement.measurement_name,
            "frequency_data": frequency_data,
            "raw_data": raw_data,
            "s11_data": s11_data,
            "s12_data": s12_data,
            "s21_data": s21_data,
            "s22_data": s22_data,
            "created_at": measurement.created_at,
        }
