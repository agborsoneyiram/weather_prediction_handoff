def classify_rain_sensor(rain_value):
    """
    Classify the rain sensor's raw analog reading.

    The thresholds are provisional and should be calibrated
    using actual sensor observations.
    """

    if rain_value < 300:
        return "dry"

    elif rain_value < 1000:
        return "light"

    elif rain_value < 1800:
        return "moderate"

    else:
        return "heavy"