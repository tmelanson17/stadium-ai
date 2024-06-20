import Jetson.GPIO as GPIO



class GPIOControl:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.pwm_channels = [[15,16],[18,19], [21,22]]
        self.enable_channel = 13
        for group in self.pwm_channels:
            for channel in group:
                GPIO.setup(channel, GPIO.OUT)
        GPIO.setup(self.enable_channel, GPIO.OUT)
        self.reset()

    def reset(self):
        for group in self.pwm_channels:
            for channel in group:
                GPIO.output(channel, GPIO.LOW)
        GPIO.output(self.enable_channel, GPIO.LOW)

    def execute_command(self, idx):
        GPIO.output(self.enable_channel, GPIO.HIGH)
        if idx==0:
            GPIO.output(self.pwm_channels[0][1], GPIO.HIGH)
            GPIO.output(self.pwm_channels[1][0], GPIO.HIGH)
        elif idx==1:
            GPIO.output(self.pwm_channels[0][1], GPIO.HIGH)
            GPIO.output(self.pwm_channels[1][1], GPIO.HIGH)
        elif idx==2:
            GPIO.output(self.pwm_channels[0][1], GPIO.HIGH)
            GPIO.output(self.pwm_channels[2][0], GPIO.HIGH)
        elif idx==3:
            GPIO.output(self.pwm_channels[0][1], GPIO.HIGH)
            GPIO.output(self.pwm_channels[2][1], GPIO.HIGH)

    # TODO: switch buttons

if __name__ == "__main__":
    import time
    ctl = GPIOControl()
    while True:
        str_num = input()
        num = int(str_num)
        print(num)
        ctl.execute_command(num)
        time.sleep(0.1)
        ctl.reset()


