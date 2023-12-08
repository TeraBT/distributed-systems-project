# Block: get-predict-for-timestamp

<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Generates a POSIX timestamp for which the traffic system shall be updated. For development - fixed value.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>predictFor : int</li>
    </ul></td>
  </tr>
</table>

# Block: analyze-input-data
<table>
  <tr>
    <th>Type</th>
    <td>Parallel compound</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Generates predictions for traffic and air quality, counts emergency vehicles</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>

# Block: get-camera-list
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Gets a list of all cameras in the system</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>cameraIds : list[string]</li>
    </ul></td>
  </tr>
</table>

# Block: analyze-data-per-camera
<table>
  <tr>
    <th>Type</th>
    <td>ParallelFor compound</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Predicts traffic development for each camera and counts emergency vehicles. Stores the results in DynamoDB.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Iterators</th>
    <td><ul>
        <li>cameraId : string</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>

# Block: get-images
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Gets the latest <i>x</i> images for a prediction time for a specific camera</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>predictFor : int</li>
        <li>cameraId : string</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>imageUris : dict[int, string] (Note: key = POSIX timestamp, value = URI)</li>
    </ul></td>
  </tr>
</table>

# Block: count-all-vehicles
<table>
  <tr>
    <th>Type</th>
    <td>Parallel compound</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Counts (and predicts) normal vehicles, counts emergency vehicles</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>predictFor : int</li>
        <li>imageUris : dict[int, string]</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>trafficPrediction : int</li>
        <li>emergencyVehicleCount : int</li>
    </ul></td>
  </tr>
</table>

# Block: count-cars
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Analyzes the given images and counts how many cars there are in each image.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>imageUris : dict[int, string]</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>carCounts : dict[int, int]</li>
    </ul></td>
  </tr>
</table>

# Block: predict-car-count
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Uses historic car counts to predict traffic for a specific time in the future.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>predictFor : int</li>
        <li>carCounts : dict[int, int]</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>carCountPrediction : int</li>
    </ul></td>
  </tr>
</table>

# Block: count-emergency-vehicles
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Counts the number of emergency vehicles in the latest image from a camera.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>imageUris : dict[int, string]</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>emergencyVehicleCount : int</li>
    </ul></td>
  </tr>
</table>

# Block: update-vehicle-counts
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Stores the generated traffic predictions and data in the DynamoDB table</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>predictFor : int</li>
        <li>cameraId : string</li>
        <li>carCountPrediction : int</li>
        <li>emergencyVehicleCount : int</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>

# Block: get-station-list
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Gets a list of all sensor stations in the system</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>stationIds : list[string]</li>
    </ul></td>
  </tr>
</table>

# Block: analyze-data-per-station
<table>
  <tr>
    <th>Type</th>
    <td>ParallelFor compound</td>
  </tr>
  <tr>
    <th>Description</th>
    <td></td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Iterators</th>
    <td><ul>
        <li>stationIds : list[string]</li>
    </ul>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>

# Block: predict-air-quality
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Gets the latest <i>x</i> measurements for a prediction time for a specific sensor station, predicts the air quality for the future and stores the result in the DynamoDB table</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>predictFor : int</li>
        <li>stationId : int</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>

# Block: get-street-list
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Gets a list of all streets in the system</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>streedIds : list[string]</li>
    </ul></td>
  </tr>
</table>

# Block: check-limits-per-street
<table>
  <tr>
    <th>Type</th>
    <td>ParallelFor compound</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Check the limits (traffic, emergency vehicles, air quality) for each street.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Iterators</th>
    <td><ul>
        <li>streedIds : list[string]</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>

# Block: check-limits
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Checks the limits for a street and stores the results in the DynamoDB table. Information which cameras and which sensor stations shall be used comes from DynamoDB.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>predictFor : int</li>
        <li>streetId : string</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>

# Block: get-section-list
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Gets a list of all sections in the system</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
        <li>sectionIds : list[string]</li>
    </ul></td>
  </tr>
</table>

# Block: determine-info-per-section
<table>
  <tr>
    <th>Type</th>
    <td>ParallelFor compound</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Determine the information to display (speed limit, extra information) per street section.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
    </ul></td>
  </tr>
  <tr>
    <th>Iterators</th>
    <td><ul>
        <li>sectionIds : list[string]</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>

# Block: determine-info
<table>
  <tr>
    <th>Type</th>
    <td>Base function</td>
  </tr>
  <tr>
    <th>Description</th>
    <td>Determines the new traffic information to display for a specific street section and stores the result in DynamoDB. Information on which street data affects the section comes from DynamoDB.</td>
  </tr>
  <tr>
    <th>Inputs</th>
    <td><ul>
        <li>predictFor : int</li>
        <li>sectionId : string</li>
    </ul></td>
  </tr>
  <tr>
    <th>Outputs</th>
    <td><ul>
    </ul></td>
  </tr>
</table>
