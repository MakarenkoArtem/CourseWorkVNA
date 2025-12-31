import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class FullErrModel(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'FullErrModel'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    ports = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    settings_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("settings.id"))
    ef00_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    ef00_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    ef11_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    ef11_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    #========Однопортовая===========
    detEf_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    detEf_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    #========Двухпортовая===========
    ef10_01_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    ef10_01_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er33_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er33_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er22_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er22_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er23_32_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er23_32_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    ef30_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    ef30_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er03_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er03_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    ef22_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    ef22_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    ef10_32_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    ef10_32_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er11_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er11_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er23_01_Re = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    er23_01_Im = sqlalchemy.Column(sqlalchemy.Float, nullable=True)


    def to_dict(self):
        return dict(filter(lambda item: item[0] not in ['_sa_instance_state'] , self.__dict__.items()))
