// Power Query (M) behind traffic_dashboard.pbix, Part 1 Task 4.1.
// Paste into Home > Advanced Editor. The source path points at the Windows copy of the
// repository; change it (or use Data source settings) when opening the file elsewhere.
let
    Source = Csv.Document(
        File.Contents("C:\Users\USER\OneDrive\Documents\GitHub\NUS-AI-ML-smart-city-traffic-capstone-project\part1_data_analytics\data\Metro_Interstate_Traffic_Volume.csv"),
        [Delimiter = ",", Columns = 9, Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    // Types are set with the en-US culture so decimals parse the same on any Windows locale.
    ChangedType = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"holiday", type text}, {"temp", type number}, {"rain_1h", type number},
            {"snow_1h", type number}, {"clouds_all", Int64.Type}, {"weather_main", type text},
            {"weather_description", type text}, {"date_time", type datetime},
            {"traffic_volume", Int64.Type}
        },
        "en-US"
    ),
    // The CSV writes ordinary days as the string "None"; make them real nulls.
    HolidayNoneToNull = Table.ReplaceValue(ChangedType, "None", null, Replacer.ReplaceValue, {"holiday"}),
    AddHour = Table.AddColumn(HolidayNoneToNull, "Hour", each Time.Hour([date_time]), Int64.Type),
    // 0 K readings are physically impossible and become null instead of -273.15.
    AddCelsius = Table.AddColumn(AddHour, "Temperature (C)", each if [temp] > 0 then [temp] - 273.15 else null, type number),
    AddCategory = Table.AddColumn(
        AddCelsius,
        "Traffic Category",
        each if [traffic_volume] < 4500 then "Low" else if [traffic_volume] <= 5500 then "Medium" else "High",
        type text
    )
in
    AddCategory
