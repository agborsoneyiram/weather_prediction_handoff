GET /

Returns API status.

GET /current?location=kasoa

Returns current weather.

GET /predict?location=kasoa

Returns:
{
    success,
    location,
    generated_at,
    prediction:
    {
        temperature,
        humidity,
        rainfall,
        rainfall_category
    }
}

GET /locations

Returns available locations.