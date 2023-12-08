import json
import os
from string import Template

CDK_OUTPUT_FILEPATH = os.path.join(".", "config.json")
TEMPLATE_FILEPATH = os.path.join(".", "apollo", "typeMappings.json.tpl")
OUTPUT_FILEPATH = os.path.join(".", "apollo", "typeMappings.json")

CFN_OUTPUT_MAPPING = {
    "determineinfourl": "DetermineInfoInvokeURL",
    "countcarsurl": "CountCarsInvokeURL",
    "predictairqualityurl": "PredictAirQualityInvokeURL",
    "getcameralisturl": "GetCameraListInvokeURL",
    "checklimitsurl": "CheckLimitsInvokeURL",
    "getimagesurl": "GetImagesInvokeURL",
    "getstationlisturl": "GetStationListInvokeURL",
    "predictcarcounturl": "PredictCarCountInvokeURL",
    "getstreetlisturl": "GetStreetListInvokeURL",
    "countemergencyvehiclesurl": "CountEmergencyVehiclesInvokeURL",
    "updatevehiclescounturl": "UpdateVehiclesCountInvokeURL",
    "getpredictfortimestampurl": "GetPredictForTimestampInvokeURL",
    "getsectionlisturl": "GetSectionListInvokeURL",
}


def create_type_mappings(
    cdk_output_path: os.PathLike, template_path: os.PathLike, output_path: os.PathLike
):
    with open(cdk_output_path, "r") as f:
        cdk_ouput = json.load(f)
    urls = {}
    for k, v in cdk_ouput["MainStack"].items():
        urls[CFN_OUTPUT_MAPPING[k]] = v

    with open(template_path, "r") as f:
        template = Template(f.read())

    out = template.safe_substitute(urls)

    with open(output_path, "w") as f:
        f.write(out)


if __name__ == "__main__":
    create_type_mappings(CDK_OUTPUT_FILEPATH, TEMPLATE_FILEPATH, OUTPUT_FILEPATH)
