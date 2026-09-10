def rainfall_category(value):

    if value < 2:
        return "No Rain"

    elif value < 10:
        return "Low"

    elif value < 30:
        return "Moderate"

    return "High"

def sensor_rain_category(value):
    """
    Classify HW-038 water level sensor readings
    using experimentally calibrated ADC thresholds.
    """

    if value <= 75:
        return "Dry"

    elif value <= 217:
        return "Light"

    elif value <= 442:
        return "Moderate"

    elif value <= 961:
        return "Heavy"

    return "Very Heavy"