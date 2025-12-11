from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError


def validate_freq(form, field):
    if field.data < 500:
        raise ValidationError(f"{field.label} должно(а) быть не меньше 500")
    if field.data > 50000:
        raise ValidationError(f"{field.label} должно(а) быть не больше 50000")


def validate_cnt(form, field):
    if field.data < 1:
        raise ValidationError(f"{field.label} должно(а) быть положительной")


class MeasureForm(FlaskForm):
    freq_start_mhz = FloatField("Минимальная частота", validators=[DataRequired(), validate_freq])
    freq_stop_mhz = FloatField("Максимальная частота", validators=[DataRequired(), validate_freq])
    num_freq_points = IntegerField("Число точек", validators=[DataRequired(), validate_cnt])
    rbw_khz = FloatField("RBW", validators=[DataRequired()])
    output_power_dbm = FloatField('dBm', validators=[DataRequired()])
    txtr = SelectField("Номер излучающего порта", choices=[
        (3, '3'), (6, '6')], validators=[DataRequired()])
    mode = SelectField("Тип измерений", choices=[
        (0, '1 порт'), (1, '2 порта')], validators=[DataRequired()])

    measure = SubmitField('Измерить')
