To set the voltage:
echo 72.0 > Box_user_set_voltage.txt
Can also use the OFF keyword to turn on OFF

To set the max current:
Bar: python ManualControl.py "CURR 0.4" --ip '192.168.133.201'
Box: python ManualControl.py "CURR 0.4" --ip '192.168.133.200'

To turn all of the off:
python control.py halt

To turn all ON:
python control.py light
