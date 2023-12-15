# Use cases

| ID | Task | Use case and involved access patterns |
|---|---|---|
| UC1-1 | Get camera list | Get the IDs of all cameras (APR1) |
| UC2-1 | Get images | Get the URIs of the latest (within limits, considering desired prediction time) images for a specific camera (APR2) |
| UC3-1 | Update vehicle count | Put prediction values and emergency vehicle counts for a specific camera and a specific prediction time (APW1) |
| UC4-1 | Get station list | Get the IDs of all stations (APR3) |
| UC5-1 | Predict air quality | Get the latest (within limits, considering desired prediction time) measurements for a specific station (APR4) |
| UC5-2 | Predict air quality | Put prediction value for a specific station and a specific prediction time (APW2) |
| UC6-1 | Get street list | Get the IDs of all streets (APR5) |
| UC7-1 | Check limits | Get predicition values - car count (APR7), air quality (APR8) - and emergency vehicle count for a specific prediction time and all cameras / stations that cover a specific street (APR6) |
| UC7-2 | Check limits | Get traffic capacity limit and air quality limit for a specific street (APR6) |
| UC7-3 | Check limits | Put limit analysis values for a specific street and a specific prediction time (APW3) |
| UC8-1 | Get section list | Get the IDs of all sections (APR9) |
| UC9-1 | Determine info | Get limit analysis values for a specific prediction time (APR11) and the street in which the section is placed (APR10) |
| UC9-2 | Determine info | Get default speed limit for a specific section (APR10) |
| UC9-3 | Determine info | Put speed limit and (optional) information text for a specific section and a specific prediction time (APW4) |

# Entities

<table>
    <tr>
        <th>Partition key</th>
        <th>Sort key</th>
        <th>Fields</th>
        <th>Represented entity</th>
    </tr>
    <tr>
        <td>baseEntity</td>
        <td>camera#ID</td>
        <td>-</td>
        <td>camera</td>
    </tr>
    <tr>
        <td>camera#{ID}</td>
        <td>image#{timestamp}</td>
        <td><ul>
            <li>URI
                <ul>
                    <li>type: string</li>
                    <li>value: key of image in S3 bucket</li>
                </ul>
            </li>
        </ul></td>
        <td>image</td>
    </tr>
    <tr>
        <td>camera#{ID}</td>
        <td>trafficCount#{timestamp}</td>
        <td><ul>
            <li>carCountPrediction
                <ul>
                    <li>type: number</li>
                    <li>value: predicted number of cars for the given prediction time</li>
                </ul>
            </li>
            <li>emergencyVehicleCount
                <ul>
                    <li>type: number</li>
                    <li>value: currently effective number of emergency vehicles</li>
                </ul>
            </li>
        </ul></td>
        <td>-</td>
    </tr>
    <tr>
        <td>baseEntity</td>
        <td>station#{ID}</td>
        <td>-</td>
        <td>station</td>
    </tr>
    <tr>
        <td>station#{ID}</td>
        <td>measurement#{timestamp}</td>
        <td><ul>
            <li>airQuality
                <ul>
                    <li>type: number</li>
                    <li>value: measured air quality</li>
                </ul>
            </li>
        </ul></td>
        <td>measurement</td>
    </tr>
    <tr>
        <td>station#{ID}</td>
        <td>prediction#{timestamp}</td>
        <td><ul>
            <li>airQuality
                <ul>
                    <li>type: number</li>
                    <li>value: predicted air quality</li>
                </ul>
            </li>
        </ul></td>
        <td>-</td>
    </tr>
    <tr>
        <td>baseEntity</td>
        <td>street#{ID}</td>
        <td><ul>
            <li>cameras
                <ul>
                    <li>type: list[string]</li>
                    <li>values: IDs of cameras that cover the street
                </ul>
            </li>
            <li>station
                <ul>
                    <li>type: string</li>
                    <li>value: ID of the station that covers the street</li>
                </ul>
            </li>
            <li>trafficCapacity
                <ul>
                    <li>type: number</li>
                    <li>value: traffic capacity of that street</li>
                </ul>
            </li>
            <li>airQualityLimit
                <ul>
                    <li>type: number</li>
                    <li>value: air quality limit of that street
                </ul>
            </li>
        </ul></td>
        <td>street</td>
    </tr>
    <tr>
        <td>street#{ID}</td>
        <td>info#{timestamp}</td>
        <td><ul>
            <li>trafficLoad
                <ul>
                    <li>type: number</li>
                    <li>value: a value that describes if and how overloaded the street is with traffic</li>
                </ul>                
            </li>
            <li>emergencyVehiclesActive
                <ul>
                    <li>type: boolean</li>
                    <li>value: if emergency vehicles are currently active on that street</li>
                </ul>
            </li>
            <li>airQualityLoad
                <ul>
                    <li>type: number</li>
                    <li>value: a value that describes if and how much the streets air quality limit has been exceeded</li>
                </ul>
            </li>
        </ul></td>
        <td>-</td>
    </tr>
    <tr>
        <td>baseEntity</td>
        <td>section#{ID}</td>
        <td><ul>
            <li>street
                <ul>
                    <li>type: string</li>
                    <li>value: ID of the street on which the section is placed</li>
                </ul>
            </li>
            <li>defaultSpeedLimit
                <ul>
                    <li>type: number</li>
                    <li>value: default speed limit of that section</li>
                </ul>
            </li>
        </ul></td>
        <td>section</td>
    </tr>
    <tr>
        <td>section#{ID}</td>
        <td>info#{timestamp}</td>
        <td><ul>
            <li>speedLimit
                <ul>
                    <li>type: number</li>
                    <li>value: the speed limit to display</li>
                </ul>
            </li>
            <li>text
                <ul>
                    <li>type: string</li>
                    <li>value: an optional info text to display</li>
                </ul>
            </li>
        </ul></td>
        <td>-</td>
    </tr>
</table>


# Access patterns

## Read

| ID | Use case | Method | Partition key | Sort key | Projected attributes | Consistency |
|---|---|---|---|---|---|---|
| APR1 | UC1-1 | Query | "baseEntity" | BEGINS WITH "camera#" | SK | eventual |
| APR2 | UC2-1 | Query | "camera#{ID}" | GREATER THAN "image#{beginning of timerange to consider}" | SK, URI | eventual |
| APR3 | UC4-1 | Query | "baseEntity" | BEGINS WITH "station#" | SK | eventual |
| APR4 | UC5-1 | Query | "station#{ID}" | GREATER THAN "measurement#{beginning of timerange to consider}" | SK, airQuality | eventual |
| APR5 | UC6-1 | Query | "baseEntity" | BEGINS WITH "street#" | SK | eventual |
| APR6 | UC7-1/2 | GetItem | "baseEntity" | EQUAL TO "street#{ID}" | cameras, station, trafficCapacity, airQualityLimit | eventual |
| APR7 | UC7-1 | BatchGetItem | for each camera ID: "camera#{ID}" | EQUAL TO "trafficCount#{timestamp}" | PK, carCountPrediction, emergencyVehicleCount | strong |
| APR8 | UC7-1 | GetItem | "station#{ID}" | EQUAL TO "prediction#{ID}" | airQuality | strong | 
| APR9 | UC8-1 | Query | "baseEntity" | BEGINS WITH "section#" | SK | eventual |
| APR10 | UC9-1/2| GetItem | "baseEntity" | EQUAL TO "section#{ID}" | street, defaultSpeedLimit | eventual |
| APR11 | UC9-1 | GetItem | "street#{ID}" | EQUAL TO "info#{timestamp}" | trafficLoad, emergencyVehicleLoad, airQualityLoad | strong |

## Write

| ID | Use case | Method | Partition key | Sort key |
|---|---|---|---|---|
| APW1 | UC3-1 | PutItem | "camera#{ID}" | "trafficCount#{timestamp}" |
| APW2 | UC5-2 | PutItem | "station#{ID}" | "prediction#{timestamp}" |
| APW3 | UC7-3 | PutItem | "street#{ID}" | "info#{timestamp}" |
| APW4 | UC9-3 | PutItem | "section#{ID}" | "info#{timestamp}" |