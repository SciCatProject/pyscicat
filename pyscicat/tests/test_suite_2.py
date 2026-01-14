from pathlib import Path
import urllib
import json

import requests_mock
from ..client import ScicatClient

from ..model import (
    DataFile,
    RawDataset,
    OrigDatablock,
    Ownable,
)

global test_datasets

local_url = "http://localhost:3000/api/v3/"
test_dataset_files = {
    "raw": "../../examples/data/ingestion_simulation_dataset_ess_raw_dataset.json",
    "derived": "../../examples/data/ingestion_simulation_dataset_ess_derived_dataset.json",
    "published_data": "../../examples/data/published_data.json",
}
test_datasets = {}


def set_up_test_environment(mock_request):

    # global test_datasets

    # load test data
    for name, path in test_dataset_files.items():
        data_file_path = Path(__file__).parent.joinpath(path).resolve()
        with open(data_file_path, "r") as fh:
            test_datasets[name] = json.load(fh)

    mock_request.post(
        local_url + "Users/login",
        json={"id": "a_token"},
    )


def set_up_mock_raw_dataset(mock_request):
    data = test_datasets["raw"]

    mock_request.post(
        local_url + "Datasets",
        json={**{"pid": data["id"]}, **data["dataset"]},
    )

    encoded_pid = urllib.parse.quote_plus(data["id"])
    mock_request.post(
        local_url + "Datasets/" + encoded_pid + "/origdatablocks",
        json={
            "size": data["orig_datablock"]["size"],
            "datasetId": data["id"],
            "dataFileList": data["orig_datablock"]["dataFileList"],
        },
    )

    return data


def set_up_mock_derived_dataset(mock_request):
    data = test_datasets["derived"]

    mock_request.post(
        local_url + "Datasets",
        json={**{"pid": data["id"]}, **data["dataset"]},
    )

    encoded_pid = urllib.parse.quote_plus(data["id"])
    mock_request.post(
        local_url + "Datasets/" + encoded_pid + "/origdatablocks",
        json={
            "size": data["orig_datablock"]["size"],
            "datasetId": data["id"],
            "dataFileList": data["orig_datablock"]["dataFileList"],
        },
    )

    return data


def set_up_mock_published_data(mock_request):
    data = test_datasets["published_data"]

    mock_url = local_url + "PublishedData"
    print("Mock : " + mock_url)
    mock_request.get(
        mock_url,
        json=data,
    )

    return data


def test_scicat_ingest_raw_dataset():
    with requests_mock.Mocker() as mock_request:
        set_up_test_environment(mock_request)
        data = set_up_mock_raw_dataset(mock_request)
        scicat = ScicatClient(
            base_url=local_url,
            username="Zaphod",
            password="heartofgold",
        )
        assert (
            scicat._token == "a_token"
        ), "scicat client set the token given by the server"

        ownable = Ownable(**data["ownable"])

        # Create Dataset
        dataset = RawDataset(**data["dataset"], **ownable.dict())
        created_dataset_pid = scicat.create_dataset(dataset)

        assert created_dataset_pid == data["dataset"] | {"pid": data["id"]}

        # origDatablock with DataFiles
        origDataBlock = OrigDatablock(
            size=data["orig_datablock"]["size"],
            datasetId=created_dataset_pid["pid"],
            dataFileList=[
                DataFile(**file) for file in data["orig_datablock"]["dataFileList"]
            ],
            chkAlg="sha2",
            **ownable.dict()
        )
        created_origdatablock = scicat.create_dataset_origdatablock(origDataBlock)
        assert len(created_origdatablock["dataFileList"]) == len(
            data["orig_datablock"]["dataFileList"]
        )


def test_scicat_ingest_derived_dataset():
    with requests_mock.Mocker() as mock_request:
        set_up_test_environment(mock_request)
        data = set_up_mock_derived_dataset(mock_request)
        scicat = ScicatClient(
            base_url=local_url,
            username="Zaphod",
            password="heartofgold",
        )
        assert (
            scicat._token == "a_token"
        ), "scicat client set the token given by the server"

        ownable = Ownable(**data["ownable"])

        # Create Dataset
        dataset = RawDataset(**data["dataset"], **ownable.dict())
        created_dataset_pid = scicat.create_dataset(dataset)

        assert created_dataset_pid == data["dataset"] | {"pid": data["id"]}

        # origDatablock with DataFiles
        origDataBlock = OrigDatablock(
            size=data["orig_datablock"]["size"],
            datasetId=created_dataset_pid["pid"],
            dataFileList=[
                DataFile(**file) for file in data["orig_datablock"]["dataFileList"]
            ],
            chkAlg="sha2",
            **ownable.dict()
        )
        created_origdatablock = scicat.create_dataset_origdatablock(origDataBlock)
        assert len(created_origdatablock["dataFileList"]) == len(
            data["orig_datablock"]["dataFileList"]
        )


def test_scicat_find_published_data():
    with requests_mock.Mocker() as mock_request:
        set_up_test_environment(mock_request)
        data = set_up_mock_published_data(mock_request)
        scicat = ScicatClient(
            base_url=local_url,
            username="Zaphod",
            password="heartofgold",
        )
        assert (
            scicat._token == "a_token"
        ), "scicat client set the token given by the server"

        returned_data = scicat.find_published_data()

        assert len(data) == len(returned_data)
        assert data == returned_data
