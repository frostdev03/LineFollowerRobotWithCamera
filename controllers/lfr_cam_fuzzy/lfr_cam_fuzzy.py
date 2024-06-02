from controller import Robot
import numpy as np
import cv2
import skfuzzy as fuzz
import skfuzzy.control as ctl

def get_center(im):
    gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cX = 0
    cY = 0
    valid_contours = []
    height, width = im.shape[:2]
    for c in contours:
        area = cv2.contourArea(c)
        if 500 < area < 5000:  # Filter contours by area size
            x, y, w, h = cv2.boundingRect(c)
            if y + h > height // 2:  # Only consider contours in the bottom half of the image
                valid_contours.append(c)

    if valid_contours:
        c = max(valid_contours, key=cv2.contourArea)  # Select the largest valid contour
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(im, (cX, cY), 3, (0, 255, 0), -1)

        # Draw only valid contours
        cv2.drawContours(im, valid_contours, -1, (0, 0, 255), 5)

    # Center line
    center_x = width // 2
    cv2.line(im, (center_x, 0), (center_x, height), (255, 0, 0), 2)

    return cX, cY, im


# Input
error = ctl.Antecedent(np.arange(-210, 211, 1), 'Error')
delta_error = ctl.Antecedent(np.arange(-210, 211, 1), 'Delta Error')

# Output
left_motor_speed = ctl.Consequent(np.arange(0, 6.29, 0.1), 'Left Motor Speed')
right_motor_speed = ctl.Consequent(np.arange(0, 6.29, 0.1), 'Right Motor Speed')

# Membership functions for error
error['highly_negative'] = fuzz.trimf(error.universe, [-210, -210, -105])
error['negative'] = fuzz.trimf(error.universe, [-210, -105, 0])
error['mid'] = fuzz.trimf(error.universe, [-105, 0, 105])
error['positive'] = fuzz.trimf(error.universe, [0, 105, 210])
error['highly_positive'] = fuzz.trimf(error.universe, [105, 210, 210])

# Membership functions for delta_error
delta_error['highly_negative'] = fuzz.trimf(delta_error.universe, [-210, -210, -105])
delta_error['negative'] = fuzz.trimf(delta_error.universe, [-210, -105, 0])
delta_error['mid'] = fuzz.trimf(delta_error.universe, [-105, 0, 105])
delta_error['positive'] = fuzz.trimf(delta_error.universe, [0, 105, 210])
delta_error['highly_positive'] = fuzz.trimf(delta_error.universe, [105, 210, 210])

# Membership functions for motor speed
left_motor_speed['very_slow'] = fuzz.trimf(left_motor_speed.universe, [0, 0, 1.57])
left_motor_speed['slow'] = fuzz.trimf(left_motor_speed.universe, [0.79, 1.57, 3.14])
left_motor_speed['medium'] = fuzz.trimf(left_motor_speed.universe, [1.57, 3.14, 4.71])
left_motor_speed['fast'] = fuzz.trimf(left_motor_speed.universe, [3.14, 4.71, 6.28])
left_motor_speed['very_fast'] = fuzz.trimf(left_motor_speed.universe, [4.71, 6.28, 6.28])

right_motor_speed['very_slow'] = fuzz.trimf(right_motor_speed.universe, [0, 0, 1.57])
right_motor_speed['slow'] = fuzz.trimf(right_motor_speed.universe, [0.79, 1.57, 3.14])
right_motor_speed['medium'] = fuzz.trimf(right_motor_speed.universe, [1.57, 3.14, 4.71])
right_motor_speed['fast'] = fuzz.trimf(right_motor_speed.universe, [3.14, 4.71, 6.28])
right_motor_speed['very_fast'] = fuzz.trimf(right_motor_speed.universe, [4.71, 6.28, 6.28])

# Define rules
rules = [
    ctl.Rule(error['highly_negative'] & delta_error['highly_negative'], (left_motor_speed['very_fast'], right_motor_speed['very_slow'])),
    ctl.Rule(error['highly_negative'] & delta_error['negative'], (left_motor_speed['fast'], right_motor_speed['slow'])),
    ctl.Rule(error['highly_negative'] & delta_error['mid'], (left_motor_speed['medium'], right_motor_speed['slow'])),
    ctl.Rule(error['highly_negative'] & delta_error['positive'], (left_motor_speed['medium'], right_motor_speed['medium'])),
    ctl.Rule(error['highly_negative'] & delta_error['highly_positive'], (left_motor_speed['slow'], right_motor_speed['fast'])),

    ctl.Rule(error['negative'] & delta_error['highly_negative'], (left_motor_speed['fast'], right_motor_speed['very_slow'])),
    ctl.Rule(error['negative'] & delta_error['negative'], (left_motor_speed['medium'], right_motor_speed['slow'])),
    ctl.Rule(error['negative'] & delta_error['mid'], (left_motor_speed['medium'], right_motor_speed['medium'])),
    ctl.Rule(error['negative'] & delta_error['positive'], (left_motor_speed['slow'], right_motor_speed['medium'])),
    ctl.Rule(error['negative'] & delta_error['highly_positive'], (left_motor_speed['slow'], right_motor_speed['fast'])),

    ctl.Rule(error['mid'] & delta_error['highly_negative'], (left_motor_speed['medium'], right_motor_speed['fast'])),
    ctl.Rule(error['mid'] & delta_error['negative'], (left_motor_speed['medium'], right_motor_speed['medium'])),
    ctl.Rule(error['mid'] & delta_error['mid'], (left_motor_speed['medium'], right_motor_speed['medium'])),
    ctl.Rule(error['mid'] & delta_error['positive'], (left_motor_speed['medium'], right_motor_speed['medium'])),
    ctl.Rule(error['mid'] & delta_error['highly_positive'], (left_motor_speed['medium'], right_motor_speed['fast'])),

    ctl.Rule(error['positive'] & delta_error['highly_negative'], (left_motor_speed['slow'], right_motor_speed['medium'])),
    ctl.Rule(error['positive'] & delta_error['negative'], (left_motor_speed['slow'], right_motor_speed['medium'])),
    ctl.Rule(error['positive'] & delta_error['mid'], (left_motor_speed['medium'], right_motor_speed['medium'])),
    ctl.Rule(error['positive'] & delta_error['positive'], (left_motor_speed['slow'], right_motor_speed['fast'])),
    ctl.Rule(error['positive'] & delta_error['highly_positive'], (left_motor_speed['very_slow'], right_motor_speed['very_fast'])),

    ctl.Rule(error['highly_positive'] & delta_error['highly_negative'], (left_motor_speed['slow'], right_motor_speed['fast'])),
    ctl.Rule(error['highly_positive'] & delta_error['negative'], (left_motor_speed['slow'], right_motor_speed['medium'])),
    ctl.Rule(error['highly_positive'] & delta_error['mid'], (left_motor_speed['medium'], right_motor_speed['medium'])),
    ctl.Rule(error['highly_positive'] & delta_error['positive'], (left_motor_speed['slow'], right_motor_speed['fast'])),
    ctl.Rule(error['highly_positive'] & delta_error['highly_positive'], (left_motor_speed['very_slow'], right_motor_speed['very_fast']))
]

# Control system
rms_ctrl = ctl.ControlSystem(rules)
lms_ctrl = ctl.ControlSystem(rules)

# Simulation
rms_sim = ctl.ControlSystemSimulation(rms_ctrl)
lms_sim = ctl.ControlSystemSimulation(lms_ctrl)

# Initialize Robot
robot = Robot()
timestep = int(robot.getBasicTimeStep())

cam = robot.getDevice("camera")
cam.enable(timestep)

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Main loop:
previous_error = 0
max_speed = 6.28

while robot.step(timestep) != -1:
    img = cam.getImageArray()
    if img is not None:
        img = np.asarray(img, dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        img = cv2.resize(img, (0, 0), fx=3.5, fy=3.5)
        crop_img = cv2.flip(img, 1)

        cX, cY, im = get_center(crop_img)
        cv2.imshow("Image", im)
        cv2.waitKey(15)
        
        width = im.shape[1]
        center_point = width // 2
        error = cX - center_point
        delta_error = error - previous_error
        previous_error = error

        # Fuzzy inference
        rms_sim.input['Error'] = error
        rms_sim.input['Delta Error'] = delta_error
        lms_sim.input['Error'] = error
        lms_sim.input['Delta Error'] = delta_error

        rms_sim.compute()
        lms_sim.compute()

        right_speed = rms_sim.output['Right Motor Speed']
        left_speed = lms_sim.output['Left Motor Speed']

        # Set motor velocities
        left_motor.setVelocity(left_speed)
        right_motor.setVelocity(right_speed)
        
        # Debug
        print("=------------------------------=")
        print(f"Center point: {center_point}")
        print(f"Contour center X: {cX}")
        print(f"Error: {error}")
        print(f"Delta Error: {delta_error}")
        print(f"Left Motor Speed: {left_speed}")
        print(f"Right Motor Speed: {right_speed}")

# Exit cleanup
cv2.destroyAllWindows()