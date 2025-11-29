from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError


def validate_freq(form, field):
    if field.data <= 0:
        raise ValidationError(f"{field.label} должно(а) быть больше нуля")


class MeasureForm(FlaskForm):
    minFreq = FloatField("Минимальная частота", validators=[DataRequired(), validate_freq])
    maxFreq = FloatField("Максимальная частота", validators=[DataRequired(), validate_freq])
    pointCnt = IntegerField("Число точек", validators=[DataRequired(), validate_freq])
    rbw = FloatField("RBW", validators=[DataRequired()])
    dbm = FloatField('dBm', validators=[DataRequired()])
    txtr = IntegerField("txtr", validators=[DataRequired(), validate_freq])
    mode = SelectField("Тип измерений", choices=[
        (0, '1 порт'), (1, '2 порта')], validators=[DataRequired()])

    measure = SubmitField('Измерить')
    calibrate = SubmitField('Калибровать')